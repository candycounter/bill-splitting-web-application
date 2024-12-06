import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "11uWndBb_NB73Ppq-zvUFaNHq38C0TI4fUTf9gp_rKqQ"
SAMPLE_RANGE_NAME = "Lidl 10/30/23!A:Z"


def create_worksheet(service, spreadsheet_id, sheet_title):
    try:
        # Create a request to add a new sheet
        requests = [
            {
                "addSheet": {
                    "properties": {
                        "title": sheet_title,
                        "gridProperties": {
                            "rowCount": 100,
                            "columnCount": 26
                        }
                    }
                }
            }
        ]

        # Execute the request
        body = {"requests": requests}
        response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        # Extract sheetId from response
        sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
        print(f"Sheet '{sheet_title}' created successfully!")
        return sheet_id
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def apply_formatting(service, spreadsheet_id, sheet_id):
    try:
        # Define the format requests
        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": int(sheet_id),
                        "startRowIndex": 0,
                        "endRowIndex": 100,  # Adjust as needed
                        "startColumnIndex": 0,
                        "endColumnIndex": 26  # Adjust as needed
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields": "userEnteredFormat(horizontalAlignment, verticalAlignment, wrapStrategy)"
                }
            }
        ]
        
        # Apply formatting
        body = {
            "requests": requests
        }
        response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        print("Formatting applied successfully!")
        return response
    except Exception as e:
        print(f"An error occurred while applying formatting: {e}")
        return None
def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)
    sheets = service.spreadsheets()
    result = sheets.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    
    values = result.get("values", [])
    
    for row in values:
      print(row)
  except HttpError as error:
      print(error)


def send_to_sheets(receipt_df, cost_df, date, restaurant, total_cost, payer):
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)
    
        
    sheet_name = restaurant + " " + str(date)
    sheet_id = create_worksheet(service, SAMPLE_SPREADSHEET_ID, sheet_name)
    print(sheet_id)
    
    receipt_data = receipt_df.values.tolist()
    receipt_header = receipt_df.columns.tolist()
    
    other_data = [['Total Cost', str(total_cost)], ['Payer', payer]]
    
    for row in receipt_data:
      temp = ", ".join(row[2])
      row[2] = temp
    
    print(receipt_data)
    receipt_data.insert(0, receipt_header)
    print(receipt_data)
    
    cost_data = cost_df.values.tolist()
    cost_header = cost_df.columns.tolist()
    cost_data.insert(0, cost_header)
    print(cost_data)
    
    sheet_range = f"{sheet_name}!A1"
          
          # Update the worksheet with receipt data
    service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=sheet_range,
        valueInputOption="RAW",
        body={"values": receipt_data}
    ).execute()
    
    sheet_range = f"{sheet_name}!E1"
    
    service.spreadsheets().values().update(
      spreadsheetId=SAMPLE_SPREADSHEET_ID,
      range=sheet_range,
      valueInputOption="RAW",
      body={"values": cost_data}
    ).execute()
    
    sheet_range = f"{sheet_name}!H1"
    
    service.spreadsheets().values().update(
      spreadsheetId=SAMPLE_SPREADSHEET_ID,
      range=sheet_range,
      valueInputOption="RAW",
      body={"values": other_data}
    ).execute()
    
    apply_formatting(service, SAMPLE_SPREADSHEET_ID, sheet_id)

  except HttpError as error:
    print(error)
  # print(receipt_data)
if __name__ == "__main__":
  main()