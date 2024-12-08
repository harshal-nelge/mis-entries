import streamlit as st
import os
import time
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

SERVICE_ACCOUNT_FILE = 'service_account.json'
SHEET_ID = '1jTrZR3YE0sp-BxKXWsSFkjsEPfFANMfb2lwZwl56iHg'

# Define the scope of access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Authenticate using the service account file
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
gc = gspread.authorize(credentials)

# Open the Google Sheet
worksheet = gc.open_by_key(SHEET_ID).sheet1

# Configure the generative AI API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type="application/pdf"):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    st.write("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    st.write("...all files ready")

def main():
    st.title("Alegria MIS EntryManager")

    # Upload PDF file
    uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

    # Input receipt book number
    receipt_book_number = st.text_input("Enter Receipt Book Number")

    if st.button("Process and Insert Data"):
        if uploaded_file and receipt_book_number:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.read())

            # Upload file to Gemini
            files = [upload_to_gemini(uploaded_file.name)]

            # Wait for files to become active
            wait_for_files_active(files)

            # Set up the model configuration
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
            )

            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            files[0],
                            "generate a json for each page in pdf with fields Registration Date(Date in DD/MM/YY format), Receipt Number, Participant Name, Event Name(Event Code followed by Event Name), Participant Phone Number, Participant Email ID, Amount Paid, Volunteer Code"
                        ],
                    },
                ]
            )

            response = chat_session.send_message("generate json for each page in pdf")
            json_data = response.text

            # Prepare the data to be written to the sheet
            data_to_insert = []

            parsed_data = json.loads(json_data)
            for entry in parsed_data:
                row = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
                    'iaditya22it@student.mes.ac.in',  # Email Address
                    entry['Registration Date'],  # Registration Date
                    receipt_book_number,  # Receipt Book Number
                    entry['Receipt Number'],  # Receipt Number
                    entry['Participant Name'],  # Participant Name
                    entry['Event Name'],  # Event Name
                    None,  # College Name (null)
                    entry['Participant Phone Number'],  # Participant Phone Number
                    entry['Participant Email ID'],  # Participant Email ID
                    entry['Amount Paid'],  # Amount Paid
                    entry['Volunteer Code'],  # Volunteer Code
                ]
                data_to_insert.append(row)

            # Write the data to Google Sheets
            worksheet.insert_rows(data_to_insert, 2)  # Starts inserting at row 2 (skipping header)

            st.success(f"{len(data_to_insert)} rows added successfully!")
        else:
            st.error("Please upload a PDF file and enter the receipt book number.")

if __name__ == "__main__":
    main()
