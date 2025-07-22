import sys

from . import f_value
from .load_file_from_e01 import method_load_file_from_e01
from Registry import Registry

def method_get_user_f_value_data_with_rid(cwd, partition_id, rid):
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
                    print("------------------------------")
                    print("value.name()")
                    print(value.name())
                    if int(value.name(), 16) == int(rid):
                        print("+++++++++++++++")
                        print(f"Key Name: {value.name()}")
                        print("---------------")
                        for unit_type_1 in value.values():
                            if unit_type_1.name() == "F":
                                print(f"Value Name: {unit_type_1.name()}")
                                print(f"Value Type: {unit_type_1.value_type_str()}")
                                f_val = f_value.method_get_f_value_data(cwd, unit_type_1.raw_data())
                                print(f_val)
                                flag = 1

            return {
                "f_val": f_val,
                "status": "passed"
            }







    except FileNotFoundError:
        print(f"Error: The file was not found.")
    except Registry.RegistryParse.ParseException as e:
        print(f"Error parsing the registry file: {e}")