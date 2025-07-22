import io
import sys
import traceback
from email import message_from_bytes
from pathlib import Path

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver


def get_path_spec(e01_path, partition_id, file_path):
    """Creates a dfvfs path specification object."""
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
        location=file_path,
        parent=partition_path_spec)

    return fs_path_spec


def list_files_in_directory(directory_path_spec):
    """
    Lists all files within a given directory path specification.
    Returns a list of filenames.
    """
    try:
        file_object = resolver.Resolver.OpenFileObject(directory_path_spec)
        filenames = []
        for entry in file_object.entries:
            # We only want to process files, not subdirectories
            if entry.entry_type == definitions.FILE_ENTRY_TYPE_FILE:
                filenames.append(entry.name)
        return filenames
    except Exception as e:
        print(f"[-] Error listing directory {directory_path_spec.location}: {e}")
        return []


def read_file_contents(file_path_spec):
    """Reads the full content of a file given its path specification."""
    try:
        file_object = resolver.Resolver.OpenFileObject(file_path_spec)
        return file_object.read()
    except Exception as e:
        print(f"[-] Error reading file {file_path_spec.location}: {e}")
        return None


def main_email_analysis_workflow(cwd, partition_id, username):
    """
    Main function to demonstrate listing and reading email files.
    """
    print(f"[*] Starting email analysis for user: {username}")

    # Construct the path to the user's Inbox directory for Windows Vista/7/10
    # NOTE: This path is case-sensitive for dfvfs
    inbox_directory_path = f"/Users/{username}/AppData/Local/Microsoft/Windows Mail/Local Folders/Inbox"

    e01_path = str(Path(cwd) / "uploads" / "upload.E01")

    # 1. Get the path spec for the directory itself
    directory_spec = get_path_spec(e01_path, partition_id, inbox_directory_path)
    print(f"[*] Attempting to list contents of: {inbox_directory_path}")

    # 2. List all the .eml files in the directory
    email_filenames = list_files_in_directory(directory_spec)

    if not email_filenames:
        print("[-] No email files found in the directory or directory could not be accessed.")
        return

    print(f"[+] Found {len(email_filenames)} email files.")

    # 3. Loop through each filename, read it, and parse it
    all_email_text = []
    for filename in email_filenames[:5]:  # Limiting to first 5 for demonstration
        print(f"\n--- Processing: {filename} ---")

        # Construct the full path for the individual email file
        email_file_path = f"{inbox_directory_path}/{filename}"
        email_file_spec = get_path_spec(e01_path, partition_id, email_file_path)

        # Read the raw .eml file content
        email_data = read_file_contents(email_file_spec)

        if email_data:
            # Parse the .eml file using Python's email library
            msg = message_from_bytes(email_data)

            subject = msg.get('Subject', 'No Subject')
            from_addr = msg.get('From', 'No Sender')
            to_addr = msg.get('To', 'No Recipient')

            # Extract the text body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            print(f"  From: {from_addr}")
            print(f"  To: {to_addr}")
            print(f"  Subject: {subject}")

            # Aggregate the text for the LLM
            email_text = f"From: {from_addr}\nTo: {to_addr}\nSubject: {subject}\n\n{body}\n\n---\n\n"
            all_email_text.append(email_text)

    print("\n[*] Finished processing emails.")
    # At this point, you would send the 'all_email_text' variable to the LLM
    # For example:
    # summary = call_llm_api("".join(all_email_text))
    # return summary


# Example usage:
if __name__ == '__main__':
    # Replace with your actual project directory and user details
    current_working_directory = "C:\\path\\to\\your\\project"
    partition = 1
    user_to_analyze = "Wes Mantooth"

    main_email_analysis_workflow(current_working_directory, partition, user_to_analyze)

