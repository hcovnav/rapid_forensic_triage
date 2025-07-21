import traceback
from pathlib import Path

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver



def get_sam_path_spec(e01_path, partition_id):
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


def method_extract_SAM_registry_file(cwd, partition_id):


    try:
        partition_id = str(partition_id)
        e01_path = cwd + "\\uploads\\upload.E01"
        print("e01_path")
        print(e01_path)
        output_dir = cwd + "\\uploads\\partitions\\" + partition_id
        print("output_dir")
        print(output_dir)
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        output_path = cwd + "\\uploads\\partitions\\" + partition_id + "\\extracted_SAM"
        print("output_path")
        print(output_path)
        fs_path_spec = get_sam_path_spec(e01_path, partition_id)

        extract_file_to_local(fs_path_spec, output_path)
    except:
        traceback.print_exc()
        print("[-] Failed to extract SAM registry.")
        return {"status": "failed", "message": "Failed to extract SAM registry."}
    else:
        return {"status": "passed", "message": "SAM registry extracted."}


