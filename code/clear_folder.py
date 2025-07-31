import os
import shutil


def clear_folder_contents(folder_path):
    """
    Deletes all files and subdirectories within a given folder.

    Args:
        folder_path (str): The absolute or relative path to the folder.

    Returns:
        None
    """
    # --- Safety Check ---
    # First, check if the folder actually exists to avoid errors.
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at '{folder_path}'")
        return

    print(f"Starting to clear contents of folder: '{folder_path}'")

    # --- Iterate and Delete ---
    # os.listdir() returns a list of all entry names in the directory.
    for filename in os.listdir(folder_path):
        # os.path.join() creates a full, OS-compatible path (e.g., 'uploads/image.jpg')
        file_path = os.path.join(folder_path, filename)

        try:
            # Check if the current item is a file or a symbolic link
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # os.unlink() is equivalent to os.remove()
                print(f"  - Deleted file: {file_path}")

            # Check if the current item is a directory
            elif os.path.isdir(file_path):
                # shutil.rmtree() deletes a directory and all its contents.
                shutil.rmtree(file_path)
                print(f"  - Deleted directory: {file_path}")

        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

    print(folder_path)
    print("checking if empty")
    print(os.listdir(folder_path))
    try:
        os.remove(folder_path + "\\upload.E01")
    except Exception as e:
        print(f"Failed to delete upload.E01. Reason: {e}")

    print("checking if empty again")
    print(os.listdir(folder_path))
    print("Folder contents cleared successfully.")

