from typing import Union
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from msal import ConfidentialClientApplication
import requests

AUTHORITY="<AUTHORITY>"
CLIENT_ID="<CLIENT_ID>"
CLIENT_SECRET="<CLIENT_SECRET>"
REDIRECT_URI = "<REDIRECT_URI>"
SCOPES = ["https://graph.microsoft.com/.default"]

app = FastAPI()
microsoft_app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)

@app.get("/login")
async def login():
    auth_url = microsoft_app.get_authorization_request_url(
        SCOPES, redirect_uri=REDIRECT_URI
    )
    return RedirectResponse(auth_url)

@app.get("/get_embded_report")
def route() -> Union[dict, dict]:
    token = get_token()
    print(token)
    report_id = "<REPORT_ID>"
    report = get_report_by_id(report_id, token)
    return report



def get_token() -> Union[str, dict]:

    
    # Acquire a token
    result = microsoft_app.acquire_token_for_client(scopes=SCOPES)

    # Check and use the token
    if "access_token" in result:
        return result["access_token"]
    else:
        return result.get("error_description")

def get_report_by_id(report_id: str, access_token: str) -> dict:
    URL = f"https://api.powerbi.com/v1.0/myorg/reports/{report_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(URL, headers=headers)

    if response.status_code == 200:
        print("Report Data:", response.json())
    else:
        print("Error:", response.status_code, response.text)
    return  {}

