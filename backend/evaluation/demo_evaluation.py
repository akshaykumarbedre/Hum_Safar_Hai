"""
Demo script to show evaluation framework working with mock responses
"""
import sys
import os
import json
import asyncio

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.run_evaluation import evaluate_keyword_match, evaluate_with_llm_as_judge

async def mock_evaluation_demo():
    """Demo the evaluation framework with mock agent responses."""
    print("Agent Evaluation Framework Demo")
    print("=" * 50)
    
    # Load the actual dataset
    with open('evaluation/evaluation_dataset.json', 'r') as f:
        dataset = json.load(f)
    
    # Mock responses that would come from the agent
    mock_responses = {
        "NW-001": "Your total net worth is ₹658,305. This includes assets like mutual funds, EPF, and securities minus liabilities like loans. The US securities portion shows ₹30,613 as requested.",
        "EXP-001": "Based on your spending breakdown for the last 90 days, your top 3 categories are: 1) Miscellaneous (₹45,000), 2) Financial Services (₹32,000), and 3) Bills & Utilities (₹28,000).",
        "INV-001": "Yes, some of your mutual funds are underperforming the 10% XIRR benchmark. Specifically, HDFC Small Cap fund is showing 7.2% returns and Aditya Birla Sun Life Mid Cap is at 8.5% XIRR.",
        "GEN-001": "Under Section 80C of the Income Tax Act for FY 2024-2025, you can claim deductions up to ₹1.5 lakh for investments in EPF, ELSS mutual funds, Public Provident Fund (PPF), life insurance premiums, and Tuition Fees for children's education."
    }
    
    results = []
    print(f"Running evaluation demo for {len(dataset)} test cases...\n")
    
    for i, test_case in enumerate(dataset):
        print(f"--- Test Case {i+1}: {test_case['question_id']} ---")
        print(f"Question: {test_case['question']}")
        print(f"User: {test_case['user_id']}")
        
        # Get mock response
        mock_answer = mock_responses.get(test_case['question_id'], "No response available")
        print(f"Mock Response: {mock_answer}")
        
        # Evaluate the answer
        result = {"status": "FAIL", "details": ""}
        if test_case['evaluation_type'] == 'keyword_match':
            passed = await evaluate_keyword_match(mock_answer, test_case['answer_keywords'])
            result['status'] = "PASS" if passed else "FAIL"
            result['details'] = f"Keywords found: {[k for k in test_case['answer_keywords'] if k.lower() in mock_answer.lower()]}"
        elif test_case['evaluation_type'] == 'llm_as_judge':
            eval_result = await evaluate_with_llm_as_judge(
                test_case['question'], 
                mock_answer, 
                test_case['answer_keywords'],
                model="gemini-2.0-flash"
            )
            result['status'] = "PASS" if eval_result['score'] >= 4 else "FAIL"
            result['details'] = f"LLM Judge Score: {eval_result['score']}/5 - {eval_result['reason']}"
        
        results.append({**test_case, "generated_answer": mock_answer, "result": result})
        print(f"Result: {result['status']} - {result['details']}")
        print()
    
    # Generate report
    print("--- EVALUATION REPORT ---")
    passed_count = sum(1 for r in results if r['result']['status'] == 'PASS')
    total_count = len(results)
    pass_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"Overall Pass Rate: {passed_count}/{total_count} ({pass_rate:.2f}%)")
    
    if passed_count < total_count:
        print("\nFailed Test Cases:")
        for r in results:
            if r['result']['status'] == 'FAIL':
                print(f"- ID: {r['question_id']}, Purpose: {r['purpose']}")
    else:
        print("\n🎉 All test cases passed!")
    
    print("\nDetailed Results:")
    for r in results:
        print(f"- {r['question_id']}: {r['result']['status']} ({r['evaluation_type']})")

if __name__ == "__main__":
    asyncio.run(mock_evaluation_demo())