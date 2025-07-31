import os
import json
import sys
import traceback
from email import message_from_bytes
from pathlib import Path

from .collect_user_emails import method_get_user_email_paths

import google.generativeai as genai

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver


def get_gemini_api_key(cwd):
    """Reads the Gemini API key from a local config.json file."""
    try:
        with open(Path(cwd) / "config.json", "r") as config_file:
            config = json.load(config_file)
        return config.get("gemini_api_key", "YOUR_API_KEY_HERE")
    except FileNotFoundError:
        print("[-] config.json not found. Please ensure it exists and contains your API key.")
        return "YOUR_API_KEY_HERE"


def get_path_spec(e01_path, partition_id, file_path):
    """Creates a dfvfs path specification object for a given path."""
    resolved_e01_path = str(Path(e01_path).resolve())
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
        location=file_path,
        parent=partition_path_spec)
    return fs_path_spec


def read_file_contents(file_path_spec):
    """
    Reads the full raw byte content of a file given its path specification.
    This function must return bytes for the email parser to work correctly.
    """
    try:
        file_object = resolver.Resolver.OpenFileObject(file_path_spec)
        return file_object.read()
    except Exception as e:
        print(f"[-] Error reading file {file_path_spec.location}: {e}")
        return None


def parse_eml_file(email_data):
    """
    Parses raw .eml byte data and extracts key fields into a formatted string.
    """
    if not email_data:
        return None

    try:
        # This function now correctly receives a bytes object.
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

        return f"Date: {date}\nFrom: {from_addr}\nTo: {to_addr}\nSubject: {subject}\n\nBody:\n{body}\n"
    except Exception as e:
        traceback.print_exc()
        print(f"[-] Error parsing email: {e}")
        return None


def get_email_summary_from_llm(email_texts, gemini_api_key):
    """
    Sends the aggregated email text to the Gemini API and returns the summary.
    """
    if not email_texts:
        return "No email content was provided to analyze."

    if gemini_api_key == "YOUR_API_KEY_HERE":
        return "Error: Gemini API Key has not been set in the script or config.json."

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        full_email_content = "\n---\n".join(email_texts)

        prompt = f"""
        You are a forensic analyst assistant. Your task is to summarize a collection of emails.
        Based on the following email data, provide a concise summary covering these points:
        1. **Key Correspondents:** Who are the main people the user is communicating with?
        2. **Main Topics of Discussion:** What are the primary subjects being discussed?
        3. **Potentially Suspicious Activity:** Are there any emails that seem unusual, out of place, or mention sensitive topics like passwords, confidential data, or illicit activities? Be specific but objective.

        Here is the email data:
        ---
        {full_email_content}
        """

        print("[*] Sending request to Gemini API...")
        response = model.generate_content(prompt)
        print("[+] Received response from Gemini API.")

        return response.text

    except Exception as e:
        print(f"[-] An error occurred with the Gemini API: {e}")
        traceback.print_exc()
        return f"Error during AI analysis: {e}"


def method_analyze_user_emails(cwd, partition_id, email_paths):
    """
    Main workflow to read, parse, and summarize emails from a list of paths.
    """
    print(f"[*] Starting analysis of {len(email_paths)} emails.")
    e01_path = str(Path(cwd) / "uploads" / "upload.E01")

    parsed_email_texts = []
    for path in email_paths[:10]:  # Limiting to 10 emails for the PoC
    #for path in email_paths:
        print(f"[*] Reading: {path}")
        spec = get_path_spec(e01_path, partition_id, path)
        email_content = read_file_contents(spec)

        if email_content:
            parsed_text = parse_eml_file(email_content)
            if parsed_text:
                parsed_email_texts.append(parsed_text)

    print(parsed_email_texts)
    # The API key is retrieved and the LLM is called *after* parsing.
    gemini_api_key = get_gemini_api_key(cwd)
    summary = get_email_summary_from_llm(email_texts=parsed_email_texts, gemini_api_key=gemini_api_key)

    return {"status": "passed", "summary": summary}


def email_analysis(cwd, partition_id, username):

    email_file_paths = method_get_user_email_paths(cwd=cwd, partition_id=partition_id, username=username)

    result = method_analyze_user_emails(cwd=cwd, partition_id=partition_id, email_paths=email_file_paths)

    return result