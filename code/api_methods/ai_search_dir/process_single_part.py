from ..get_usernames_and_rids import method_get_usernames_and_rids
from ..get_volume_information import method_get_volume_information
from ..check_partitions import method_get_partitions_with_windows
from ..get_user_f_value_flags_with_rid import method_get_user_f_value_flags_with_rid
from ..get_user_f_value_data_with_rid import method_get_user_f_value_data_with_rid
from ..get_user_v_value_data_with_rid import method_get_user_v_value_data_with_rid
from ..collect_user_emails import method_get_user_emails


selected_tools = [
    method_get_usernames_and_rids,
    method_get_volume_information,
    method_get_partitions_with_windows,
    method_get_user_f_value_flags_with_rid,
    method_get_user_f_value_data_with_rid,
    method_get_user_v_value_data_with_rid,
    method_get_user_emails
]


import google.generativeai as genai

tool_map = {func.__name__: func for func in selected_tools}

def process_part(part, cwd, e01_path):
    if not hasattr(part, 'function_call') or not part.function_call:
        return {"type": "no_function_call", "text": part.text}

    function_call = part.function_call
    function_name = function_call.name

    print(f"\n--- Gemini wants to call function: '{function_name}' ---")

    if function_name in tool_map:
        func_to_call = tool_map[function_name]
        gemini_args = dict(function_call.args)
        print(f"Gemini's arguments (before override): {gemini_args}")

        if 'partition_id' in gemini_args:
            try:
                gemini_args['partition_id'] = int(gemini_args['partition_id'])
            except (ValueError, TypeError):
                print(f"Warning: Could not cast partition_id '{gemini_args['partition_id']}' to int.")

        if 'cwd' in func_to_call.__code__.co_varnames:
            gemini_args['cwd'] = cwd
            print(f"Overriding 'cwd' with application context: {cwd}")

        if 'e01_path' in func_to_call.__code__.co_varnames and 'e01_path' not in gemini_args:
            gemini_args['e01_path'] = e01_path

        try:
            result = func_to_call(**gemini_args)
            ret = genai.protos.Part(
                function_response=genai.protos.FunctionResponse(
                    name=function_name,
                    response={"result": result},
                )
            )
        except Exception as e:
            error_message = f"An error occurred while executing the function '{function_name}': {e}"
            print(error_message)
            return {"ai_response": error_message, "status": "failed"}
        else:
            return {"type": "function_call", "data": ret}
    else:
        print(f"Error: Model requested an unknown function: '{function_name}'")
        return {"status": "failed", "unknown function": function_name}

