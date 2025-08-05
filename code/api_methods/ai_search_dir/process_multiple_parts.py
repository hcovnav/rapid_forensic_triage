from .process_single_part import process_part
def process_parts(response, cwd, e01_path):
    ret = []
    for part in response.candidates[0].content.parts:
        rpart = process_part(part, cwd, e01_path)
        ret.append(rpart)

    ret_error = [x for x in ret if x and x.get("status") == "failed"]
    if len(ret_error) > 0:
        return {"status": "failed", "error": ret_error}
    ret_function_call = [x for x in ret if x and x.get("type") == "function_call"]
    ret_text = [x for x in ret if x and x.get("type") != "function_call"]


    if len(ret_function_call) == 0:
        ret_text = [x.get("text") for x in ret_text]
        return {"function_call":"no", "data":ret_text}
    else:
        ret_function_call = [x.get("data") for x in ret_function_call]
        return {"function_call":"yes", "data":ret_function_call}


