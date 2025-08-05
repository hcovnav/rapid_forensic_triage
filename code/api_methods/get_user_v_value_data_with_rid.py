from . import v_value
from Registry import Registry

def method_get_user_v_value_data_with_rid(cwd, partition_id, rid):
    """Extracts and parses the V value data for a specific user from the SAM hive.

    This function orchestrates the process of reading the SAM hive from the
    extracted partition files, locating the specific user account key by its
    Relative ID (RID), and then passing the raw binary V value data to a
    specialized parser (v_value.py). The user/rid key is located within "SAM/Domains/Account/Users"

    Args:
        cwd (str): The current working directory of the main application.
        partition_id (int or str): The identifier of the partition containing
            the SAM hive.
        rid (int or str): The Relative ID of the target user whose V value
            is to be parsed.

    Returns:
        dict: A dictionary containing the status of the operation. On success,
              the status is "passed" and it includes the parsed V value data
              under the 'v_val' key. On failure, it returns a dictionary
              with a "failed" status and an error message.
    """
    print("rid")
    print(rid)
    try:
        registry_file = cwd + "\\uploads\\partitions\\" + str(partition_id) + "\\extracted_SAM"
        with open(registry_file, "rb") as f:
            registry = Registry.Registry(f)
            run_key = registry.open("SAM\\Domains\\Account\\Users")
            flag = 0
            v_val = {}
            for value in run_key.subkeys():
                if flag == 1:
                    break
                if value.name() != "Names":
                    if int(value.name(), 16) == int(rid):
                        print(f"Key Name: {value.name()}")
                        for unit_type_1 in value.values():
                            if unit_type_1.name() == "V":
                                print(f"Value Name: {unit_type_1.name()}")
                                v_val = v_value.method_get_v_value_data(cwd, unit_type_1.raw_data())
                                print(v_val)
                                flag = 1
            return {
                "v_val": v_val,
                "status": "passed"
            }

    except FileNotFoundError:
        print(f"Error: The file '{registry_file}' was not found.")
        return {"status": "failed", "message": "SAM file not found."}
    except Registry.RegistryParse.ParseException as e:
        print(f"Error parsing the registry file: {e}")
        return {"status": "failed", "message": f"Registry Parse Error: {e}"}

