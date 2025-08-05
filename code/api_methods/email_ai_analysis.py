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
from .common import get_gemini_api_key


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
        # Using capitalized Resolver as confirmed by user testing.
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
    """Processes a list of email paths to generate an AI-powered summary.

    This function serves as the core workflow for the email analysis feature.
    It takes a list of file paths, reads each email from the E01 image,
    parses the content, aggregates the text, and sends it to the Gemini API
    for summarization.

    Args:
        cwd (str): The current working directory of the main application.
        partition_id (int or str): The identifier of the partition where the
            emails reside.
        email_paths (list): A list of full string paths to the .eml files
            within the evidence image.

    Returns:
        dict: A dictionary containing the status of the operation and the
              'summary' text returned by the LLM.
    """
    print(f"[*] Starting analysis of {len(email_paths)} emails.")
    e01_path = str(Path(cwd) / "uploads" / "upload.E01")

    parsed_email_texts = []
    # Limiting to 10 emails for the PoC to ensure timely response
    for path in email_paths[:10]:
        print(f"[*] Reading: {path}")
        spec = get_path_spec(e01_path, partition_id, path)
        email_content = read_file_contents(spec)

        if email_content:
            parsed_text = parse_eml_file(email_content)
            if parsed_text:
                parsed_email_texts.append(parsed_text)

    gemini_api_key = get_gemini_api_key(cwd)
    summary = get_email_summary_from_llm(email_texts=parsed_email_texts, gemini_api_key=gemini_api_key)

    return {"status": "passed", "summary": summary}


def email_analysis(cwd, partition_id, username):
    """Orchestrates the full email analysis process for a given user.

    This is a high-level wrapper function that first discovers all email
    paths for a specified user and then passes that list to the main
    analysis function to generate the AI summary.

    Args:
        cwd (str): The current working directory of the main application.
        partition_id (int or str): The identifier of the partition to search.
        username (str): The username of the target user profile.

    Returns:
        dict: A dictionary containing the status of the operation and the
              final 'summary' text generated by the AI model.
    """
    email_file_paths = method_get_user_email_paths(cwd=cwd, partition_id=partition_id, username=username)

    result = method_analyze_user_emails(cwd=cwd, partition_id=partition_id, email_paths=email_file_paths)

    return result
