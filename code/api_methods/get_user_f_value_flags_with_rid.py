from . import f_value_flags
from Registry import Registry

def method_get_user_f_value_flags_with_rid(cwd, partition_id, rid):
    """Extracts and decodes the UAC flags from a user's F value.

    This function locates a user within the extracted SAM hive by their
    Relative ID (RID). It then finds the corresponding F value, a binary
    data blob, and passes it to a helper module (f_value_flags) to parse
    the data and decode the User Account Control (UAC) flags into a
    human-readable list. The user/rid key is located within "SAM/Domains/Account/Users"

    Args:
        cwd (str): The current working directory of the main application, used
            to construct the path to the extracted SAM hive.
        partition_id (int or str): The identifier of the partition from which
            the SAM hive was extracted.
        rid (int or str): The Relative ID of the target user.

    Returns:
        dict: A dictionary containing the status of the operation. On success,
              the status is "passed" and it includes the decoded flag data
              under the 'f_val' key. On failure, the status is "failed".
    """
    print("rid")
    print(rid)
    try:
        registry_file = cwd + "\\uploads\\partitions\\" + str(partition_id) + "\\extracted_SAM"
        with open(registry_file, "rb") as f:
            registry = Registry.Registry(f)
            run_key = registry.open("SAM\\Domains\\Account\\Users")
            flag = 0
            f_val = {}
            for value in run_key.subkeys():
                if flag == 1:
                    break
                if value.name() != "Names":
                    if int(value.name(), 16) == int(rid):
                        print(f"Key Name: {value.name()}")
                        for unit_type_1 in value.values():
                            if unit_type_1.name() == "F":
                                print(f"Value Name: {unit_type_1.name()}")
                                f_val = f_value_flags.method_get_f_value_flags(cwd, unit_type_1.raw_data())
                                print(f_val)
                                flag = 1

            # Final check to ensure the parsed data corresponds to the requested RID
            if "rid" in f_val:
                if str(f_val["rid"]) == str(rid):
                    return {
                        "f_val": f_val,
                        "status": "passed"
                    }

            return {
                "f_val": f_val, # May be empty or incorrect on failure
                #"status": "failed"
            }

    except FileNotFoundError:
        print(f"Error: The file '{registry_file}' was not found.")
        return {"status": "failed", "message": "SAM file not found."}
    except Registry.RegistryParse.ParseException as e:
        print(f"Error parsing the registry file: {e}")
        return {"status": "failed", "message": f"Registry Parse Error: {e}"}
