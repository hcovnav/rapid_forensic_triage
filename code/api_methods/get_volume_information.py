import os
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver

def get_ewf_handle(e01_path):
    """Creates a dfvfs file object handle for an E01 evidence file.

    This helper function builds the necessary dfvfs path specification stack
    to open a file-like object for the raw E01 image container.

    Args:
        e01_path (str): The path to the .E01 file.

    Returns:
        dfvfs.file_io.file_io.FileIO: A dfvfs file-like object representing
            the E01 image, or raises an exception on failure.
    """
    # Wrap the actual OS file path first
    os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS,
        location=e01_path
    )

    # Then wrap it in an EWF path spec
    ewf_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EWF,
        parent=os_path_spec
    )

    # Open EWF file object
    # Using capitalized Resolver as confirmed by user testing.
    file_object = resolver.Resolver.OpenFileObject(ewf_path_spec)
    return file_object

def method_get_volume_information(e01_path: str):
    """Retrieves the total size of an E01 evidence image.

    This function opens the specified .E01 file and seeks to the end to
    determine its total size, returning the value in both bytes and
    megabytes. This is typically the first step after a file upload to
    provide the user with basic information about the evidence.

    Args:
        e01_path (str): The full, absolute path to the .E01 evidence file.

    Returns:
        dict: A dictionary containing the status of the operation. On success,
              the status is "passed" and it includes 'size_bytes' and 'size_MB'.
              On failure, the status is "failed".
    """
    print("[*] Opening E01 image...")

    try:
        ewf_object = get_ewf_handle(e01_path)

        # Get image size by seeking to the end of the file-like object
        ewf_object.seek(0, os.SEEK_END)
        size = ewf_object.get_offset()

        print(f"[+] E01 image size: {size:,} bytes ({size / (1024 ** 2):.2f} MB)")
        return {
            "status": "passed",
            "size_bytes": size,
            "size_MB": round(size/(1024 ** 2),2)
        }
    except Exception as e:
        print(f"[!] Failed to open image: {e}")
        return {
            "status": "failed",
        }
