"""
Agent Evaluation Runner

This script loads the evaluation dataset, runs each test case against the
orchestrated agent system, and reports on its performance.
"""
import os
import sys
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Our Application Imports ---
from src.fi_mcp_data_access import FIMCPDataAccess
from src.orchestration.adk_orchestrator import create_financial_orchestrator
# We need to import the runner logic from main.py or move it to a shared location
# For now, let's assume it's available or redefined here.
from main import call_agent_async 
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent
from google.genai import types

class EvaluationRating(BaseModel):
    """Pydantic model for LLM judge evaluation rating."""
    rating: int = Field(description="Rating from 1 to 5, where 1 is very poor and 5 is excellent", ge=1, le=5)
    reason: str = Field(description="Detailed explanation for the rating")

async def evaluate_keyword_match(generated_answer: str, answer_keywords: list) -> bool:
    """Checks if all expected keywords are in the generated answer."""
    return all(keyword.lower() in generated_answer.lower() for keyword in answer_keywords)

def create_llm_judge_agent(model: str) -> Agent:
    """Create an LLM judge agent with structured output using Pydantic."""
    return Agent(
        name="LLM_Judge_Agent",
        model=model,
        description=(
            "You are an expert evaluator for financial AI responses. "
            "Your job is to rate the quality and accuracy of an AI agent's answer to a financial question. "
            "Consider factors like: accuracy, completeness, relevance, clarity, and usefulness. "
            "Respond ONLY with a JSON object containing a rating (1-5) and explanation."
        ),
        instruction=(
            "Evaluate the quality of the AI response on a scale of 1-5:\n"
            "1 = Very Poor (incorrect, irrelevant, or harmful)\n"
            "2 = Poor (mostly incorrect or unhelpful)\n"
            "3 = Average (partially correct but lacking important details)\n"
            "4 = Good (mostly correct and helpful)\n"
            "5 = Excellent (accurate, complete, and very helpful)\n\n"
            "Respond ONLY with a JSON object in this format: "
            '{"rating": <number>, "reason": "<detailed explanation>"}'
        ),
        output_schema=EvaluationRating,
        output_key="evaluation_result"
    )

async def evaluate_with_llm_as_judge(question: str, generated_answer: str, criteria: list, model: str = "gemini-2.0-flash") -> dict:
    """Uses ADK LLM agent to evaluate the quality of a response with structured output."""
    try:
        # Create the LLM judge agent
        judge_agent = create_llm_judge_agent(model)
        
        # Setup session service for the judge
        session_service = InMemorySessionService()
        app_name = "llm_judge_app"
        session_id = "judge_session"
        user_id = "judge_user"
        
        # Create session
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Create runner for judge agent
        runner = Runner(agent=judge_agent, app_name=app_name, session_service=session_service)
        
        # Prepare the evaluation prompt
        evaluation_prompt = f"""
Please evaluate the following AI response:

**Question:** {question}

**Expected Keywords/Criteria:** {', '.join(criteria)}

**AI Response:** {generated_answer}

Rate this response on a scale of 1-5 considering accuracy, completeness, relevance, and helpfulness.
"""
        
        # Get evaluation from judge agent
        print(f"  [LLM Judge] - Evaluating response for question: '{question}'")
        content = types.Content(role='user', parts=[types.Part(text=evaluation_prompt)])
        
        final_response = None
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                break
        
        if final_response:
            try:
                # Parse the structured response
                import json
                evaluation_data = json.loads(final_response)
                rating = evaluation_data.get("rating", 1)
                reason = evaluation_data.get("reason", "No reason provided")
                
                print(f"  [LLM Judge] - Rating: {rating}/5 - {reason}")
                return {"score": rating, "reason": reason}
            except json.JSONDecodeError:
                print(f"  [LLM Judge] - Failed to parse JSON response: {final_response}")
                # Fallback to keyword matching
                is_correct = await evaluate_keyword_match(generated_answer, criteria)
                return {"score": 4 if is_correct else 2, "reason": "Fallback to keyword matching due to JSON parse error"}
        else:
            print("  [LLM Judge] - No response received from judge agent")
            # Fallback to keyword matching
            is_correct = await evaluate_keyword_match(generated_answer, criteria)
            return {"score": 4 if is_correct else 2, "reason": "Fallback to keyword matching due to no response"}
            
    except Exception as e:
        print(f"  [LLM Judge] - Error during evaluation: {str(e)}")
        # Fallback to keyword matching
        is_correct = await evaluate_keyword_match(generated_answer, criteria)
        return {"score": 4 if is_correct else 2, "reason": f"Fallback to keyword matching due to error: {str(e)}"}


async def main():
    """Main evaluation function."""
    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

    with open('evaluation/evaluation_dataset.json', 'r') as f:
        dataset = json.load(f)

    results = []
    print(f"Starting evaluation for {len(dataset)} test cases...")

    for i, test_case in enumerate(dataset):
        print(f"\n--- Running Test Case {i+1}/{len(dataset)}: {test_case['question_id']} ---")
        
        # 1. Setup agent for the specific user
        dal = FIMCPDataAccess(phone_number=test_case['user_id'])
        orchestrator_agent = create_financial_orchestrator(dal, model="gemini-2.0-flash")
        
        # 2. Setup session service and create session
        session_service = InMemorySessionService()
        app_name = "eval_app"
        session_id = f"eval_session_{i}"
        
        session = await session_service.create_session(
            app_name=app_name,
            user_id=test_case['user_id'],
            session_id=session_id
        )
        
        runner = Runner(agent=orchestrator_agent, app_name=app_name, session_service=session_service)

        # 3. Get the generated answer
        generated_answer = await call_agent_async(
            query=test_case['question'],
            runner=runner,
            user_id=test_case['user_id'],
            session_id=session_id
        )

        # 4. Evaluate the answer
        result = {"status": "FAIL", "details": ""}
        if test_case['evaluation_type'] == 'keyword_match':
            passed = await evaluate_keyword_match(generated_answer, test_case['answer_keywords'])
            result['status'] = "PASS" if passed else "FAIL"
        elif test_case['evaluation_type'] == 'llm_as_judge':
            eval_result = await evaluate_with_llm_as_judge(
                test_case['question'], 
                generated_answer, 
                test_case['answer_keywords'],
                model="gemini-2.0-flash"
            )
            result['status'] = "PASS" if eval_result['score'] >= 4 else "FAIL"
            result['details'] = f"LLM Judge Score: {eval_result['score']}/5 - {eval_result['reason']}"

        results.append({**test_case, "generated_answer": generated_answer, "result": result})
        print(f"--- Result for {test_case['question_id']}: {result['status']} ---")

    # 5. Print Final Report
    print("\n\n--- EVALUATION REPORT ---")
    passed_count = sum(1 for r in results if r['result']['status'] == 'PASS')
    total_count = len(results)
    pass_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"Overall Pass Rate: {passed_count}/{total_count} ({pass_rate:.2f}%)")
    
    print("\nFailed Test Cases:")
    for r in results:
        if r['result']['status'] == 'FAIL':
            print(f"- ID: {r['question_id']}, Purpose: {r['purpose']}")
    
    # 6. Save results to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(os.path.dirname(__file__), 'result')
    os.makedirs(results_dir, exist_ok=True)
    
    result_filename = f"ev_result_{timestamp}.json"
    result_filepath = os.path.join(results_dir, result_filename)
    
    # Create comprehensive result summary
    evaluation_summary = {
        "evaluation_metadata": {
            "timestamp": timestamp,
            "total_test_cases": total_count,
            "passed_count": passed_count,
            "failed_count": total_count - passed_count,
            "pass_rate_percentage": pass_rate
        },
        "test_results": results,
        "summary": {
            "failed_test_cases": [
                {
                    "question_id": r['question_id'],
                    "purpose": r['purpose'],
                    "question": r['question'],
                    "answer_keywords": r.get('answer_keywords', []),
                    "generated_answer": r['generated_answer'],
                    "failure_reason": r['result'].get('details', 'No specific reason provided')
                }
                for r in results if r['result']['status'] == 'FAIL'
            ]
        }
    }
    
    with open(result_filepath, 'w', encoding='utf-8') as f:
        json.dump(evaluation_summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n--- Results saved to: {result_filepath} ---")

if __name__ == "__main__":
    asyncio.run(main())