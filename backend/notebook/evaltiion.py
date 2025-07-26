from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> Sending Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                break
        print(f"\n<<< Agent Response: {final_response_text}")
        return final_response_text
    except Exception as e:
        error_msg = f"Error during agent execution: {str(e)}"
        print(f"<<< Error: {error_msg}")
        return error_msg
