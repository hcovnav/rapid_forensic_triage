import os
import json
from email import message_from_bytes
import traceback
from pathlib import Path

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver

def get_path_spec(e01_path, partition_id, directory_path):
    """Creates a dfvfs path specification object for a given path."""
    try:
        resolved_e01_path = str(Path(e01_path).resolve())
    except Exception as e:
        print(f"[-] Could not resolve E01 path: {e01_path}. Error: {e}")
        return None

    os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=resolved_e01_path)

    ewf_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EWF, parent=os_path_spec)

    partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION,
        location=f"/p{partition_id}",
        parent=ewf_path_spec)

    fs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK,
        location=directory_path,
        parent=partition_path_spec)

    return fs_path_spec


def read_file_contents(file_path_spec):
    """
    Reads the full raw byte content of a file given its path specification.
    This function must return bytes for the email parser to work correctly.
    """
    try:
        # Using capitalized Resolver as confirmed by user testing.
        file_object = resolver.Resolver.OpenFileObject(file_path_spec)
        return file_object.read()
    except Exception as e:
        print(f"[-] Error reading file {file_path_spec.location}: {e}")
        return None


def get_full_path_from_path_spec(path_spec):
    """Reconstructs a full string path from a dfvfs path specification."""
    path_elements = []

    current_spec = path_spec
    while current_spec:
        if hasattr(current_spec, "location") and current_spec.location:
            path_elements.insert(0, current_spec.location)
        current_spec = current_spec.parent

    # This normalization logic might need adjustment based on the OS of the image
    return os.path.normpath(os.path.join(*path_elements)).replace("C:", "").replace("\\","/")


eml_files = []
def get_eml_files_in_directory(path_spec):
    """Recursively finds all .eml files in a directory and its subdirectories."""
    # Using capitalized Resolver as confirmed by user testing.
    file_system = resolver.Resolver.OpenFileSystem(path_spec)
    directory = file_system.GetFileEntryByPathSpec(path_spec)
    if directory:
        if hasattr(directory, "sub_file_entries"):
            for entry in directory.sub_file_entries:
                path = get_full_path_from_path_spec(entry.path_spec)
                if entry.IsDirectory():
                    get_eml_files_in_directory(entry.path_spec)
                else:
                    if entry.name.endswith(".eml"):
                        eml_files.append(path)


def method_get_user_email_paths(cwd="", username="", partition_id=""):
    """Scans a user's profile to find the paths of all .eml email files.

    This function targets the common location for Windows Mail artifacts within
    a user's profile inside an E01 image. It performs a recursive search
    to compile a comprehensive list of all .eml file paths.

    Args:
        cwd (str): The current working directory of the main application.
        username (str): The username of the target user profile.
        partition_id (int or str): The identifier of the partition to search.

    Returns:
        list: A list of strings, where each string is the full path to a
              discovered .eml file within the evidence image.
    """
    global eml_files
    eml_files = []  # Reset the global list for each call
    directory_to_list = f"/Users/{username}/AppData/Local/Microsoft/Windows Mail/Local Folders"
    e01_file_path = str(Path(cwd) / "uploads" / "upload.E01")
    if not Path(e01_file_path).exists():
        print(f"[-] E01 file not found at expected path: {e01_file_path}")
        return []

    dir_spec = get_path_spec(e01_file_path, partition_id, directory_to_list)

    if not dir_spec:
        print("[-] Failed to create path specification. Exiting.")
        return []

    get_eml_files_in_directory(dir_spec)
    return eml_files


def parse_eml_file(email_data):
    """
    Parses raw .eml byte data and extracts key fields into a dictionary.
    """
    if not email_data:
        return None

    try:
        msg = message_from_bytes(email_data)
        subject = msg.get('Subject', 'No Subject')
        from_addr = msg.get('From', 'No Sender')
        to_addr = msg.get('To', 'No Recipient')
        date = msg.get('Date', 'No Date')

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')

        return {"date":date, "subject":subject, "body":body, "from_addr":from_addr, "to_addr":to_addr}
    except Exception as e:
        traceback.print_exc()
        print(f"[-] Error parsing email: {e}")
        return None


def method_get_user_emails(cwd="", username="", partition_id=""):
    """Retrieves and parses all emails for a user, returning structured data.

    This function orchestrates the email collection process. It first calls
    method_get_user_email_paths() to discover all email file locations, then
    iterates through each path, reads the raw file content from the E01 image,
    and parses it into a structured dictionary.

    Args:
        cwd (str): The current working directory of the main application.
        username (str): The username of the target user profile.
        partition_id (int or str): The identifier of the partition to search.

    Returns:
        list: A list of dictionaries, where each dictionary represents a
              parsed email and includes its metadata, body, and source path.
    """
    paths = method_get_user_email_paths(cwd, username, partition_id)
    e01_file_path = str(Path(cwd) / "uploads" / "upload.E01")
    parsed_emails = []

    for path in paths:
        spec = get_path_spec(e01_file_path, partition_id, path)
        email_content = read_file_contents(spec)

        if email_content:
            parsed_email = parse_eml_file(email_content)
            if parsed_email:
                parsed_email['source_path'] = path
                parsed_emails.append(parsed_email)

    return parsed_emails


if __name__ == "__main__":
    cwd = "C:\\non_os\\project\\7030\\py\\finalized_v2\\web_app"
    partition_id = 1
    username = "Wes Mantooth"

    email_json_list = method_get_user_emails(cwd, username, partition_id)
    print(f"\n--- Parsed {len(email_json_list)} emails ---")
    if email_json_list:
        print(json.dumps(email_json_list[0], indent=2))
