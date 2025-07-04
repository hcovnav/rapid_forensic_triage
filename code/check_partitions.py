import dfvfs
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver

def build_fs_path_spec(e01_path, partition_id):
    os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS,
        location=e01_path
    )

    ewf_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EWF,
        parent=os_path_spec
    )

    partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION,
        location=f"/p{partition_id}",
        parent=ewf_path_spec
    )

    fs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK,
        location="/",
        parent=partition_path_spec
    )

    return fs_path_spec

def test_partitions(e01_path):
    for pid in range(1, 5):
        print(f"\n[*] Checking partition /p{pid}")
        try:
            fs_path_spec = build_fs_path_spec(e01_path, pid)
            file_entry = resolver.Resolver.OpenFileEntry(fs_path_spec)
            names = [e.name for e in file_entry.sub_file_entries]
            print(f"[+] /p{pid} contains: {names}")

            if "Documents and Settings" in names:
                print(f"Found Windows XP partition at /p{pid}")
        except Exception as e:
            print(f"[!] Partition /p{pid} not valid: {e}")

def main():
    e01_path = "C:\\non_os\\project\\7030\\py\\mantooth.E01"
    test_partitions(e01_path)

if __name__ == "__main__":
    main()
