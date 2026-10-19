from fastapi import FastAPI, Request
import os
import httpx
from fastapi.responses import RedirectResponse 
from urllib.parse import urlencode 
import secrets 

app = FastAPI()

JOBBER_CLIENT_ID = os.getenv("JOBBER_CLIENT_ID")
JOBBER_CLIENT_SECRET = os.getenv("JOBBER_CLIENT_SECRET")
JOBBER_REDIRECT_URI = os.getenv("JOBBER_REDIRECT_URI")

oauth_states = {}

@app.get("/oauth/start")
def oauth_start():
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True 
    params = {
        "client_id": JOBBER_CLIENT_ID,
        "redirect_uri": JOBBER_REDIRECT_URI,
        "response_type": "code",
        "state": state,
    }
    query_string = urlencode(params)
    auth_url = "https://api.getjobber.com/api/oauth/authorize?"+ query_string
    return RedirectResponse(auth_url)

@app.get("/")
def home():
    return {"status": "ARSW Jobber Agent is running"}

@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not state or not oauth_states.pop(state,None):
        return {"error": "Invalid OAuth state"}
    if not code:
        return {"error": "Missing code"}
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": JOBBER_CLIENT_ID,
        "client_secret": JOBBER_CLIENT_SECRET,
        "redirect_uri": JOBBER_REDIRECT_URI,
    }  
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.getjobber.com/api/oauth/token",
            data=token_data,
        )
        if response.status_code != 200:
            return {"error": "Token requets failed"}
    tokens = response.json()
    if not tokens.get("access_token"):
        return {"error": "Missing access token"}
    app.state.jobber_tokens = tokens
    return {"status": "Jobber connected"}