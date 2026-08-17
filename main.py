from fastapi import FastAPI, Request
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ARSW Jobber Agent is running"}

@app.get("/oauth/callback")
def oauth_callback(request: Request):
    code = request.query_params.get("code")
    return {"authorization_code_received": bool(code)}    