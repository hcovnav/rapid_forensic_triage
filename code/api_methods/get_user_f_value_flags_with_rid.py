from . import f_value_flags
from Registry import Registry

def method_get_user_f_value_flags_with_rid(cwd, partition_id, rid):
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
                                f_val = f_value_flags.method_get_f_value_flags(cwd, unit_type_1.raw_data())
                                print(f_val)
                                flag = 1
            if "rid" in f_val:
                if f_val["rid"] == rid:
                    return {
                        "f_val": f_val,
                        "status": "passed"
                    }

            return {
                "f_val": f_val,
                "status": "failed"
            }







    except FileNotFoundError:
        print(f"Error: The file was not found.")
    except Registry.RegistryParse.ParseException as e:
        print(f"Error parsing the registry file: {e}")