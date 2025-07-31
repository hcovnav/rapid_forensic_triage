from Registry import Registry
import os

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

def get_username_from_rid(partition_id, rid, cwd):

    link = method_get_usernames_and_rids(partition_id, cwd)
    sel = [user for user in link if str(user['account_rid'])==str(rid)]
    return sel[0]['account_name'] if len(sel)>0 else None

if __name__ == '__main__':
    cwd = os.path.dirname(os.getcwd())
    x = get_username_from_rid(partition_id = 1, rid =500, cwd=cwd)
    print(x)