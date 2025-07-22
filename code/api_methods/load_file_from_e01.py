import io
import sys
import traceback
from pathlib import Path

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver
def get_sam_path_spec(e01_path, partition_id, filepath):
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
        location=filepath,
        parent=partition_path_spec)

    return fs_path_spec


def read_file_contents(path_spec):
    print("point 1")
    print(path_spec)
    file_object = resolver.Resolver.OpenFileObject(path_spec)
    print("point 2")
    print(file_object)
    data = file_object.read()
    print("[*] First bytes:", data[:64])
    return data



def method_load_file_from_e01(cwd, partition_id, filepath="/Windows/System32/config/SAM"):


    try:
        partition_id = str(partition_id)
        e01_path = cwd + "\\uploads\\upload.E01"
        fs_path_spec = get_sam_path_spec(e01_path, partition_id, filepath)

        file_data = read_file_contents(fs_path_spec)
        return io.BytesIO(file_data)
    except:
        traceback.print_exc()
        raise Exception("Unexpected error:", sys.exc_info()[0])


