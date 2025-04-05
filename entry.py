import streamlit as st
import os
import time
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# Constants
SERVICE_ACCOUNT_FILE = 'service_account.json'
SHEET_ID = '1jTrZR3YE0sp-BxKXWsSFkjsEPfFANMfb2lwZwl56iHg' # replace with your sheet id
PDF_PATH_1 = "Alegria 2025 Final Event List - (2).pdf"  # pdf for event code and name reference

# Define the scope of access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Authenticate using the service account file
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
gc = gspread.authorize(credentials)

# Open the Google Sheet
worksheet = gc.open_by_key(SHEET_ID).sheet1

# Setup Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type="application/pdf"):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

# Streamlit UI
st.title("Event Registration Processing")

# File Upload Section
pdf_file_2 = st.file_uploader("Upload the Second PDF File", type="pdf")

# Receipt Book Number
receipt_book_number = st.text_input("Enter Receipt Book Number")

# Submit Button
if st.button("Submit"):

    if pdf_file_2 and receipt_book_number:
        # Upload the first pre-existing PDF and the second uploaded PDF
        files = [
            upload_to_gemini(PDF_PATH_1, mime_type="application/pdf"),
            upload_to_gemini(pdf_file_2, mime_type="application/pdf"),
        ]

        # Wait for files to be processed
        wait_for_files_active(files)

        # Create the model and send the request
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
                        files[1],
                        "generate a json for each page in pdf with fields Registration Date(Date in DD/MM/YY format), Receipt Number ,Participant Name ,Event Name(Event Code followed by Event Name (e.g., S06 Tug of War (B)) and strictly should be same as event list), Participant Phone Number, Participant Email ID, Amount Paid, Volunteer Code(code of volunteer(sign))",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "json\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21926\", \"Participant Name\": \"PRIYANSHU MODAK\", \"Event Name\": \"G12 Fifa Tournament PS5 (FC25)\", \"Participant Phone Number\": \"9819537274\", \"Participant Email ID\": null, \"Amount Paid\": 150, \"Volunteer Code\": \"CE18\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21927\", \"Participant Name\": \"Karan Mane\", \"Event Name\": \"G09 Clash Royale Online\", \"Participant Phone Number\": \"7718911525\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE11\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21928\", \"Participant Name\": \"Shravan Wange\", \"Event Name\": \"G09 Clash Royale Online\", \"Participant Phone Number\": \"8976038269\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE11\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21929\", \"Participant Name\": \"Deepesh Gaikwad\", \"Event Name\": \"G09 Clash Royale Online\", \"Participant Phone Number\": \"9167235690\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE11\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21930\", \"Participant Name\": \"Vedant Mali\", \"Event Name\": \"G09 Clash Royale Online\", \"Participant Phone Number\": \"8452985310\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE11\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21931\", \"Participant Name\": \"Rashad\", \"Event Name\": \"LA03 Spoken Word Poetry\", \"Participant Phone Number\": \"9136861354\", \"Participant Email ID\": null, \"Amount Paid\": 150, \"Volunteer Code\": \"CE19\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21932\", \"Participant Name\": \"Anchal\", \"Event Name\": \"G04 Ludo Offline\", \"Participant Phone Number\": \"9152992665\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE21\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21933\", \"Participant Name\": \"Shubham Pawar\", \"Event Name\": \"S10 10m Air Rifle Shooting\", \"Participant Phone Number\": \"8550985754\", \"Participant Email ID\": null, \"Amount Paid\": 150, \"Volunteer Code\": \"CE13\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21934\", \"Participant Name\": \"Kiran\", \"Event Name\": \"S21 Neo Cricket (GxB)\", \"Participant Phone Number\": \"9321159884\", \"Participant Email ID\": null, \"Amount Paid\": 150, \"Volunteer Code\": \"CE21\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21935\", \"Participant Name\": \"Anya Roy\", \"Event Name\": \"G04 Ludo Offline\", \"Participant Phone Number\": \"8390770377\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE21\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21936\", \"Participant Name\": \"Tauheed\", \"Event Name\": \"S08 Deadlift (B)\", \"Participant Phone Number\": \"8433505225\", \"Participant Email ID\": null, \"Amount Paid\": 200, \"Volunteer Code\": \"CE19\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21937\", \"Participant Name\": \"Amrita\", \"Event Name\": \"G03 Ludo Online\", \"Participant Phone Number\": \"8590406674\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE21\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21938\", \"Participant Name\": \"Aksa\", \"Event Name\": \"M02 Biz Quiz\", \"Participant Phone Number\": \"8591210825\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE19\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21939\", \"Participant Name\": \"Pratham Chinte\", \"Event Name\": \"G03 Ludo Online\", \"Participant Phone Number\": \"7045117053\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE11\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21940\", \"Participant Name\": \"Pratham Chinte\", \"Event Name\": \"G05 Chess Online\", \"Participant Phone Number\": \"7045117053\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE11\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21941\", \"Participant Name\": \"Pratham Chinte\", \"Event Name\": \"G07 Stumble Guys Online\", \"Participant Phone Number\": \"7045117053\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE11\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21942\", \"Participant Name\": \"Ubais\", \"Event Name\": \"S24 Penalty Shootout (G) 1v1\", \"Participant Phone Number\": \"9324473309\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE19\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21943\", \"Participant Name\": \"Padmapriya\", \"Event Name\": \"TW02 Graphic designing\", \"Participant Phone Number\": \"7021458413\", \"Participant Email ID\": null, \"Amount Paid\": 200, \"Volunteer Code\": \"CE21\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21944\", \"Participant Name\": \"Rishikesh\", \"Event Name\": \"G04 Ludo Offline\", \"Participant Phone Number\": \"9320124485\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE21\"}\n{\"Registration Date\": \"04/12/24\", \"Receipt Number\": \"21945\", \"Participant Name\": \"Rishikesh\", \"Event Name\": \"G10 Uno Mobile Offline\", \"Participant Phone Number\": \"9320124485\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE21\"}\n{\"Registration Date\": \"06/12/24\", \"Receipt Number\": \"21946\", \"Participant Name\": \"Megha Nair\", \"Event Name\": \"I11 The Escape Room\", \"Participant Phone Number\": \"8652566928\", \"Participant Email ID\": null, \"Amount Paid\": 200, \"Volunteer Code\": \"CE13\"}\n{\"Registration Date\": \"06/12/24\", \"Receipt Number\": \"21947\", \"Participant Name\": \"Siddhi\", \"Event Name\": \"TW07 Web application development using Python\", \"Participant Phone Number\": \"9326452188\", \"Participant Email ID\": \"siddhi_nasal_4141@gmail.com\", \"Amount Paid\": 200, \"Volunteer Code\": \"CE13\"}\n{\"Registration Date\": \"06/12/24\", \"Receipt Number\": \"21948\", \"Participant Name\": \"Aishwarya\", \"Event Name\": \"TW03 Ethical Hacking\", \"Participant Phone Number\": \"9930394040\", \"Participant Email ID\": null, \"Amount Paid\": 200, \"Volunteer Code\": \"CE13\"}\n{\"Registration Date\": \"06/12/24\", \"Receipt Number\": \"21949\", \"Participant Name\": \"Raj Pratap Singh\", \"Event Name\": \"S11 Badminton (B)\", \"Participant Phone Number\": \"8624006124\", \"Participant Email ID\": \"dhiraj505@gmail.com\", \"Amount Paid\": 200, \"Volunteer Code\": \"CE29\"}\n{\"Registration Date\": \"08/12/24\", \"Receipt Number\": \"21950\", \"Participant Name\": \"Aniket Merwade\", \"Event Name\": \"G08 8 Ball Pool Online\", \"Participant Phone Number\": \"9869672442\", \"Participant Email ID\": null, \"Amount Paid\": 100, \"Volunteer Code\": \"CE33\"}\n\n"
                    ],
                },
            ]
        )

        response = chat_session.send_message("generate json for each page in pdf")
        json_data = response.text

        # Parse the response and write to Google Sheets
        receipt_book_number = receipt_book_number

        data_to_insert = []
        parsed_data = json.loads(json_data)

        for entry in parsed_data:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'iaditya22it@student.mes.ac.in',
                entry['Registration Date'],
                receipt_book_number,
                entry['Receipt Number'],
                entry['Participant Name'],
                entry['Event Name'],
                None,
                entry['Participant Phone Number'],
                entry['Participant Email ID'],
                entry['Amount Paid'],
                entry['Volunteer Code'],
            ]
            data_to_insert.append(row)

        worksheet.insert_rows(data_to_insert, 2)

        st.success(f"{len(data_to_insert)} rows added successfully!")

    else:
        st.error("Please upload both PDFs and provide the receipt book number.")
