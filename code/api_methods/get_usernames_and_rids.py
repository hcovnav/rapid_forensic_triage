from Registry import Registry
import os

def method_get_usernames_and_rids(partition_id: int, cwd: str):
    partition_id = int(partition_id)
    """Parses the SAM hive to extract a list of local user accounts and their RIDs.

    This function locates the extracted SAM hive for a given partition, opens it,
    and navigates to the key containing user account names. It iterates through
    each user subkey to extract the username and its corresponding Relative ID (RID),
    compiling them into a list of dictionaries.
    The user keys are located within "SAM/Domains/Account/Users/Names"

    Args:
        partition_id (int or str): The identifier for the partition from which
            the SAM hive was extracted.
        cwd (str): The current working directory of the main application, used to
            construct the path to the hive file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a user
              and contains 'account_name' and 'account_rid' keys. Returns
              None if the SAM file cannot be found or parsed.
    """
    try:
        registry_file = cwd + "\\uploads\\partitions\\" + str(partition_id) + "\\extracted_SAM"

        with open(registry_file, "rb") as f:
            registry = Registry.Registry(f)

            run_key = registry.open("SAM\\Domains\\Account\\Users\\Names")
            response_info = []

            for rkey in run_key.subkeys():
                new_dict = {}
                # The RID is stored as the 'type' of the default value in the user's subkey
                rtype = rkey.values()[0].value_type()
                new_dict["account_name"] = rkey.name()
                new_dict["account_rid"] = rtype
                response_info.append(new_dict)
            return response_info

    except FileNotFoundError:
        print(f"Error: The file '{registry_file}' was not found.")
        return None
    except Registry.RegistryParse.ParseException as e:
        print(f"Error parsing the registry file: {e}")
        return None

def get_username_from_rid(partition_id, rid, cwd):
    """Retrieves a specific username by looking up its RID.

    Args:
        partition_id (int or str): The identifier for the target partition.
        rid (int or str): The Relative ID of the user to find.
        cwd (str): The current working directory of the main application.

    Returns:
        str: The account name corresponding to the given RID, or None if not found.
    """
    link = method_get_usernames_and_rids(partition_id, cwd)
    if link:
        sel = [user for user in link if str(user['account_rid']) == str(rid)]
        return sel[0]['account_name'] if len(sel) > 0 else None
    return None

if __name__ == '__main__':
    # Assumes the script is in 'api_methods', so we go up one level to the project root.
    project_root = os.path.dirname(os.path.abspath(__file__))
    cwd = os.path.dirname(project_root)

    x = get_username_from_rid(partition_id=1, rid=500, cwd=cwd)
    print(f"Username for RID 500: {x}")

    all_users = method_get_usernames_and_rids(partition_id=1, cwd=cwd)
    print("\nAll Users Found:")
    if all_users:
        for user in all_users:
            print(f"- {user['account_name']} (RID: {user['account_rid']})")

