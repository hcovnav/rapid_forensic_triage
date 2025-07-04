from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver


def get_file_entry(e01_path, partition_id, path_in_partition):
    # Build OS -> EWF -> Partition -> TSK path chain
    os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=e01_path
    )

    ewf_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EWF, parent=os_path_spec
    )

    partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION,
        location=f"/p{partition_id}",
        parent=ewf_path_spec
    )

    tsk_fs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK,
        location=path_in_partition,
        parent=partition_path_spec
    )

    file_entry = resolver.Resolver.OpenFileEntry(tsk_fs_path_spec)
    return file_entry


def list_user_profiles(e01_path):
    print("[*] Locating 'Documents and Settings'...")
    user_dir_entry = get_file_entry(e01_path, partition_id=1, path_in_partition="/Users")
 #  print(dir(user_dir_entry))
 #  print("----------------")
 #  print(user_dir_entry.sub_file_entries)

    if not user_dir_entry or not user_dir_entry.IsDirectory():
        print("[!] 'Documents and Settings' not found or not a directory.")
        return

    print("[+] Found user profiles:")
    for entry in user_dir_entry.sub_file_entries:
        if entry.IsDirectory() and not entry.name.startswith('.'):
            print(f"  - {entry.name}")


def main():
    e01_path = "C:\\non_os\\project\\7030\\py\\mantooth.E01"
    list_user_profiles(e01_path)


if __name__ == "__main__":
    main()
