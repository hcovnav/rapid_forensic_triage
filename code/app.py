import os
import json
from flask import Flask, request, render_template, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

from api_methods.get_usernames_and_rids import method_get_usernames_and_rids
from api_methods.get_usernames_and_rids import get_username_from_rid
from clear_folder import clear_folder_contents
from api_methods.get_volume_information import method_get_volume_information
from api_methods.check_partitions import method_test_partitions
from api_methods.file_extraction import method_extract_file_from_e01
from api_methods.get_user_f_value_flags_with_rid import method_get_user_f_value_flags_with_rid
from api_methods.get_user_f_value_data_with_rid import method_get_user_f_value_data_with_rid
from api_methods.get_user_v_value_data_with_rid import method_get_user_v_value_data_with_rid
from api_methods.collect_user_emails import method_get_user_emails
from api_methods.email_ai_analysis import email_analysis

# Initialize the Flask application
app = Flask(__name__)

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


current_dir = os.path.dirname(__file__)


# --- Helper Functions ---
def process_upload(filename):
    """
    Processes the uploaded file after it's saved.
    Renames the file and calls analysis methods.
    """
    print("Starting post-upload processing...")
    file_info = {
        "fileinfo": {
            "filename": filename,
        }
    }
    # Save metadata about the upload
    with open(os.path.join(UPLOAD_FOLDER, "upload_info.txt"), 'w') as f:
        f.write(json.dumps(file_info))

    # Standardize the name for processing
    original_path = os.path.join(UPLOAD_FOLDER, filename)
    new_path = os.path.join(UPLOAD_FOLDER, "upload.E01")
    os.rename(original_path, new_path)

    print("Post-upload processing complete.")

def status_jsonify(payload):
    """
    Helper to return a JSON response with a 200 or 500 status
    based on a 'status' key in the payload.
    """
    if payload.get("status") == "passed":
        return jsonify(payload)
    else:
        # Return a 500 Internal Server Error for failed status
        return jsonify(payload), 500

# --- Main Routes ---

@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles the file upload and processing."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        try:
            # Clear previous uploads and save the new file
            clear_folder_contents(UPLOAD_FOLDER)
            #return jsonify({"error": "An unknown error occurred"}), 500
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(f"Successfully saved file: {filename}")

            # Perform post-upload processing
            process_upload(filename=filename)

            # Get the URL for the new partition dashboard
            dashboard_url = url_for('dashboard')

            return jsonify({
                "success": True,
                "redirect_url": dashboard_url
            })
        except Exception as e:
            print(f"Error during file upload or processing: {e}")
            return jsonify({"error": f"An error occurred: {e}"}), 500

    return jsonify({"error": "An unknown error occurred"}), 500

# --- Web Page Views ---

@app.route('/dashboard')
def dashboard():
    """
    Displays the new dashboard for selecting a partition.
    This page will call the /api/check_partitions endpoint.
    """
    return render_template('dashboard.html')

@app.route('/web_page_view/<int:partition_id>/profiles')
def web_page_view_profiles(partition_id):
    """
    Displays the user profiles for a *specific* partition.
    This page will call the /api/partition/<partition_id>/get_usernames_and_rids endpoint.
    """
    # Pass the partition_id to the template to make it available to the frontend JS
    return render_template('profiles.html', partition_id=partition_id)

@app.route('/web_page_view/partition/<int:partition_id>/profile/<int:account_rid>')
def profile_page(partition_id, account_rid):
    """Displays a placeholder page for a specific user profile."""
    return render_template('profile.html', account_rid=account_rid, partition_id=partition_id)

# --- API Endpoints ---

@app.route('/api/check_partitions')
def api_check_partitions():
    path = os.path.join(current_dir, UPLOAD_FOLDER, "upload.E01")
    return status_jsonify(method_test_partitions(path))

@app.route('/api/partition/<int:partition_id>/extract_SAM_registry_file')
def api_extract_SAM_registry_file(partition_id):
    ret = status_jsonify(method_extract_file_from_e01(current_dir, partition_id))
    return ret


@app.route('/api/partition/<int:partition_id>/extract_Security_registry_file')
def api_extract_Security_registry_file(partition_id):
    ret = status_jsonify(method_extract_file_from_e01(current_dir, partition_id, "/Windows/System32/config/Security"))
    return ret

@app.route('/api/partition/<int:partition_id>/get_usernames_and_rids')
def api_get_usernames_and_rids(partition_id):
    """
    API endpoint to get usernames for a specific partition.
    The partition_id is passed to the underlying method.
    """
    print(f"Fetching usernames for partition: {partition_id}")
    return jsonify(method_get_usernames_and_rids(cwd=current_dir, partition_id=partition_id))



@app.route('/api/get_volume_information')
def api_get_volume_information():
    """API endpoint to get volume information."""
    path = os.path.join(current_dir, UPLOAD_FOLDER, "upload.E01")
    return status_jsonify(method_get_volume_information(path))



@app.route('/api/partition/<int:partition_id>/get_user_f_value_data_with_rid/<int:rid>')
def api_get_user_f_value_data_with_rid(partition_id, rid):
    """
    API endpoint to get usernames for a specific partition.
    The partition_id is passed to the underlying method.
    """
    print(f"Fetching usernames for partition: {partition_id}")
    return jsonify(method_get_user_f_value_data_with_rid(cwd=current_dir, partition_id=partition_id, rid=rid))



@app.route('/api/partition/<int:partition_id>/get_user_f_value_flags_with_rid/<int:rid>')
def api_get_user_f_value_flags_with_rid(partition_id, rid):
    """
    API endpoint to get usernames for a specific partition.
    The partition_id is passed to the underlying method.
    """
    print(f"Fetching usernames for partition: {partition_id}")
    return jsonify(method_get_user_f_value_flags_with_rid(cwd=current_dir, partition_id=partition_id, rid=rid))


@app.route('/api/partition/<int:partition_id>/get_user_v_value_data_with_rid/<int:rid>')
def api_get_user_v_value_data_with_rid(partition_id, rid):
    """
    API endpoint to get usernames for a specific partition.
    The partition_id is passed to the underlying method.
    """
    print(f"Fetching usernames for partition: {partition_id}")
    return jsonify(method_get_user_v_value_data_with_rid(cwd=current_dir, partition_id=partition_id, rid=rid))



@app.route('/api/partition/<int:partition_id>/get_user_emails/<int:rid>')
def api_get_user_emails(partition_id, rid):
    username = get_username_from_rid(partition_id=partition_id, rid=rid, cwd=current_dir)
    ret = method_get_user_emails(cwd=current_dir, username=username, partition_id=partition_id)
    #ret = ret[:2]
    return jsonify(ret)


@app.route('/api/partition/<int:partition_id>/email_ai_analysis/<int:rid>')
def email_ai_analysis(partition_id, rid):
    username = get_username_from_rid(partition_id=partition_id, rid=rid, cwd=current_dir)
    ret = email_analysis(cwd=current_dir, username=username, partition_id=partition_id)
    return jsonify(ret)



if __name__ == '__main__':
    app.run(debug=True, port=5001)
