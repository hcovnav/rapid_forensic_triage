from . import f_value
from .load_file_from_e01 import method_load_file_from_e01
from Registry import Registry

def method_get_user_f_value_data_with_rid(cwd, partition_id, rid):
    """Extracts and parses the F value data for a specific user from the SAM hive.

    This function orchestrates the process of reading the SAM hive from the
    E01 evidence file, locating the specific user account key by its
    Relative ID (RID), and then passing the raw binary F value data to a
    specialized parser. The user/rid key is located within "SAM/Domains/Account/Users"

    Args:
        cwd (str): The current working directory of the main application.
        partition_id (int or str): The identifier of the partition containing
            the SAM hive.
        rid (int or str): The Relative ID of the target user whose F value
            is to be parsed.

    Returns:
        dict: A dictionary containing the status of the operation. On success,
              the status is "passed" and it includes the parsed F value data
              under the 'f_val' key. On failure, the status is "failed" with
              an error message.
    """
    print("rid")
    print(rid)
    try:
        registry_file_path_in_e01 = "/Windows/System32/config/SAM"
        try:
            f = method_load_file_from_e01(cwd=cwd, partition_id=partition_id, filepath=registry_file_path_in_e01)
        except:
            return {
                "status": "failed",
                "message": "Unable to read file"
            }
        else:

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
                                f_val = f_value.method_get_f_value_data(cwd, unit_type_1.raw_data())
                                print(f_val)
                                flag = 1

            return {
                "f_val": f_val,
                "status": "passed"
            }

    except FileNotFoundError:
        print(f"Error: The file was not found.")
        return {"status": "failed", "message": "SAM file not found."}
    except Registry.RegistryParse.ParseException as e:
        print(f"Error parsing the registry file: {e}")
        return {"status": "failed", "message": f"Registry Parse Error: {e}"}

