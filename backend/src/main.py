from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from msal import ConfidentialClientApplication
import requests

security = HTTPBearer()

AUTHORITY="https://login.microsoftonline.com/<TENANT_ID>"
CLIENT_ID="CLIENT_ID"
CLIENT_SECRET="<CLIENT_SECRET>"
REDIRECT_URI = "http://localhost:8000/receive_token"
SCOPES = ["https://analysis.windows.net/powerbi/api/Report.Read.All"]
REPORT_ID = "<REPORT_ID>"
DATASET_ID = "<DATASET_ID>"

app = FastAPI()
security = HTTPBearer()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

microsoft_app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)


@app.get("/sign-in")
async def signIn():
    #  Should use microsoft_app.acquire_token_silent(scopes=SCOPES, account=None) instead. I don't have permission to use it.
    result = microsoft_app.get_authorization_request_url(scopes=SCOPES)
    return RedirectResponse(result)
    

def report_embed_url(access_token):
    response = requests.get(f"https://api.powerbi.com/v1.0/myorg/reports/{REPORT_ID}", headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })
    if response.status_code == 200:
        report = response.json()
        return  report.get("embedUrl")
    else: 
        return None

def report_embed_token(access_token):
    response = requests.post(f"https://api.powerbi.com/v1.0/myorg/reports/{REPORT_ID}/GenerateToken", json={
        "datasets": [{"id": "your-dataset-id"}],
        "reports": [{"id": REPORT_ID}]
    }, headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    })
    print(response)
    if response.status_code == 200:
        report = response.json()
        return report.get("token")
    else:
        return None

@app.get("/receive_token")
def receive_token(code: str):
    result = microsoft_app.acquire_token_by_authorization_code(
        code, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    if "error" in result:
        return {"error": result["error_description"]}
    else:
        return result["access_token"]
    
@app.get("/embed")
async def embed(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    if not token: 
        raise HTTPException(status_code=401, detail="Invalid token")
    else:
        embed_token = report_embed_token(token)
        embed_url = report_embed_url(token)
        return { "embed_token": embed_token, "embed_url": embed_url }