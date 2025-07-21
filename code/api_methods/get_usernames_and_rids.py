from Registry import Registry

def method_get_usernames_and_rids(partition_id, cwd):

    try:
        registry_file = cwd + "\\uploads\\partitions\\" + str(partition_id) + "\\extracted_SAM"

        with open(registry_file, "rb") as f:
            registry = Registry.Registry(f)

            run_key = registry.open("SAM\\Domains\\Account\\Users\\Names")
            response_info = []

            for rkey in run_key.subkeys():
                new_dict = {}
                rtype = rkey.values()[0].value_type()
                new_dict["account_name"] = rkey.name()
                new_dict["account_rid"] = rtype
                response_info.append(new_dict)
            return response_info

    except FileNotFoundError:
        print(f"Error: The file '{registry_file}' was not found.")
    except Registry.RegistryParse.ParseException as e:
        print(f"Error parsing the registry file: {e}")