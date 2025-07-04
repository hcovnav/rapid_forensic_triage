import os
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver

def get_ewf_handle(e01_path):
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
    file_object = resolver.Resolver.OpenFileObject(ewf_path_spec)
    return file_object

def main():
    e01_path = "C:\\non_os\\project\\7030\\py\\mantooth.E01"
    print("[*] Opening E01 image...")

    try:
        ewf_object = get_ewf_handle(e01_path)

        # Get image size
        ewf_object.seek(0, os.SEEK_END)
        size = ewf_object.get_offset()

        print(f"[+] E01 image size: {size:,} bytes ({size / (1024 ** 2):.2f} MB)")
    except Exception as e:
        print(f"[!] Failed to open image: {e}")

if __name__ == "__main__":
    main()
