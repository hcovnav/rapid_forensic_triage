import google.generativeai as genai
from ..common import get_gemini_api_key
from .dep import selected_tools, sys_instruction
from .process_multiple_parts import process_parts


def method_run_gemini_interaction(cwd, user_prompt, e01_path):
    final_answer = ""
    try:
        genai.configure(api_key=get_gemini_api_key(cwd))
    except Exception as e:
        print(f"Error configuring API key: {e}")
        return {"result": "Error: Could not configure the AI model."}

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        tools=selected_tools,
        system_instruction=sys_instruction
    )
    chat = model.start_chat()

    final_prompt = f"""
    User Query: "{user_prompt}"
    Current E01 Image File Path: "{e01_path}"
    Please use the available tools to answer the user's query based on the provided file path context.
    """

    response = chat.send_message(final_prompt)

    max_turns = 10
    turn_count = 0

    while turn_count < max_turns:
        turn_count += 1
        print(f"\n--- Turn {turn_count} ---")

        processed_response = process_parts(response, cwd, e01_path)

        if processed_response.get("status") == "failed":
            final_answer = processed_response.get("result", "An unspecified error occurred during tool execution.")
            break

        if processed_response["function_call"] == "yes":
            tool_results = processed_response["data"]

            print(f"--- Sending {len(tool_results)} tool result(s) back to Gemini... ---")
            response = chat.send_message(tool_results)
        else:
            print("--- Model has responded with final text. Exiting loop. ---")
            if processed_response["data"]:
                final_answer = processed_response["data"][0]
            else:
                final_answer = "Model finished without a final text response."

            break

    if turn_count >= max_turns:
        final_answer = "The AI agent reached its maximum number of turns without reaching a final answer."

    return {"result": final_answer}
