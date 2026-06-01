import os
import base64
import json
import boto3
import requests
from flask import Flask, redirect, url_for, session, render_template, request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

app = Flask(__name__)
app.secret_key = 'dia_secret_key_123'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ── Load all credentials from one file ───────────────────────
# This file is blocked by .gitignore — never pushed to GitHub
# On Render these are set as environment variables instead
CLIENT_ID     = os.environ.get('GCP_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GCP_CLIENT_SECRET')
AWS_KEY       = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET    = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION    = os.environ.get('AWS_REGION', 'ap-south-1')
S3_BUCKET     = os.environ.get('S3_BUCKET', 'dia-excel-files')

# ── If running locally, load from secrets.json ───────────────
if not CLIENT_ID:
    with open('secrets.json') as f:
        secrets      = json.load(f)
        CLIENT_ID    = secrets['GCP_CLIENT_ID']
        CLIENT_SECRET= secrets['GCP_CLIENT_SECRET']
        AWS_KEY      = secrets['AWS_ACCESS_KEY_ID']
        AWS_SECRET   = secrets['AWS_SECRET_ACCESS_KEY']
        AWS_REGION   = secrets.get('AWS_REGION', 'ap-south-1')
        S3_BUCKET    = secrets.get('S3_BUCKET', 'dia-excel-files')

REDIRECT_URI = os.environ.get(
    'REDIRECT_URI', 'http://127.0.0.1:5001/callback'
)

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/gmail.readonly'
]

@app.route('/')
def index():
    email = session.get('email')
    files = session.get('files', [])
    return render_template('index.html', email=email, files=files)

@app.route('/login')
def login():
    scope_str = ' '.join(SCOPES)
    params = {
        'client_id':     CLIENT_ID,
        'redirect_uri':  REDIRECT_URI,
        'response_type': 'code',
        'scope':         scope_str,
        'access_type':   'offline',
        'prompt':        'consent'
    }
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')

    token_resp = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code':          code,
            'client_id':     CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri':  REDIRECT_URI,
            'grant_type':    'authorization_code'
        }
    ).json()

    access_token = token_resp.get('access_token')

    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    session['email']        = user_info.get('email')
    session['access_token'] = access_token

    return redirect(url_for('index'))

@app.route('/fetch')
def fetch():
    if 'access_token' not in session:
        return redirect(url_for('login'))

    creds    = Credentials(token=session['access_token'])
    gmail    = build('gmail', 'v1', credentials=creds)
    s3       = boto3.client(
        's3',
        aws_access_key_id     = AWS_KEY,
        aws_secret_access_key = AWS_SECRET,
        region_name           = AWS_REGION
    )
    uploaded = []

    results  = gmail.users().messages().list(
        userId='me',
        q='Zomato has:attachment'
    ).execute()

    for msg in results.get('messages', []):
        detail = gmail.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()
        for part in detail.get('payload', {}).get('parts', []):
            filename = part.get('filename', '')
            if not filename.endswith(('.xlsx', '.xls')):
                continue
            att_id = part['body'].get('attachmentId')
            if not att_id:
                continue
            att = gmail.users().messages().attachments().get(
                userId='me',
                messageId=msg['id'],
                id=att_id
            ).execute()
            raw = base64.urlsafe_b64decode(att['data'])
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=f'{session["email"]}/zomato/{filename}',
                Body=raw
            )
            uploaded.append(filename)

    session['files'] = uploaded
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)