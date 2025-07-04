import os

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver


def get_sam_path_spec(e01_path, partition_id=1):
    os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=e01_path)

    ewf_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EWF, parent=os_path_spec)

    partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION,
        location=f"/p{partition_id}",
        parent=ewf_path_spec)

    fs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK,
        location="/Windows/System32/config/SAM",
        parent=partition_path_spec)

    return fs_path_spec


def extract_file_to_local(path_spec, output_path):
    print(f"[*] Extracting to {output_path}...")

    file_object = resolver.Resolver.OpenFileObject(path_spec)
    with open(output_path, "wb") as out_file:
        data = file_object.read(4096)
        while data:
            out_file.write(data)
            data = file_object.read(4096)

    print("[+] Done.")


def main():
    e01_path = "C:\\non_os\\project\\7030\\py\\mantooth.E01"
    output_path = "C:\\non_os\\project\\7030\\py\\extracted_SAM"  # You can change this
    fs_path_spec = get_sam_path_spec(e01_path)

    extract_file_to_local(fs_path_spec, output_path)


if __name__ == "__main__":
    main()
