# DIA — Data Ingestion Application

A desktop and web application that authenticates a Gmail account via OAuth2, 
fetches email attachments (CSV, XLSX, PDF) based on keyword filters, 
and uploads them to AWS S3.

---

## Features

- Gmail OAuth2 authentication — no passwords stored
- Keyword-based email search and attachment extraction
- Supports CSV, XLSX and PDF file formats
- Direct upload to AWS S3 with folder structure per user
- Desktop GUI built with Tkinter
- Web version built with Flask

---

## Tech Stack

- Python 3.9+
- Flask
- Tkinter
- Google Gmail API
- AWS S3 (boto3)
- Google Cloud Platform (OAuth2)

---

## Setup

### 1. Install dependencies
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 \
google-api-python-client boto3 flask requests python-dotenv
```

### 2. Google Cloud Setup
- Create a project on [Google Cloud Console](https://console.cloud.google.com)
- Enable Gmail API
- Create OAuth 2.0 credentials (Web Application)
- Add authorized redirect URIs:
  - `http://127.0.0.1:5001/callback` (local)
  - `https://your-app.onrender.com/callback` (hosted)
- Download `credentials.json` and place in project root

### 3. AWS Setup
- Create an S3 bucket
- Create an IAM user with `AmazonS3FullAccess`
- Generate Access Key ID and Secret Key

### 4. Create `secrets.json`
```json
{
    "GCP_CLIENT_ID": "your_client_id",
    "GCP_CLIENT_SECRET": "your_client_secret",
    "AWS_ACCESS_KEY_ID": "your_aws_key",
    "AWS_SECRET_ACCESS_KEY": "your_aws_secret",
    "AWS_REGION": "ap-south-1",
    "S3_BUCKET": "your_bucket_name"
}
```

### 5. Run desktop app
```bash
python desktop_app.py
```

### 6. Run web app locally
```bash
python app.py
```
Open `http://127.0.0.1:5001`

---

## Deployment

Hosted on [Render](https://render.com) free tier.  
Set the following environment variables on Render:
GCP_CLIENT_ID
GCP_CLIENT_SECRET
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
S3_BUCKET
REDIRECT_URI


---

## Security

- `secrets.json` and `credentials.json` are excluded via `.gitignore`
- No credentials are hardcoded in the source code
- AWS IAM user is scoped to S3 only
- Gmail access is read-only

---

## Note

This application is currently in testing phase on Google Cloud Platform. 
To log in, your Gmail must be added as a test user by the developer, 
or the app must be published on GCP OAuth consent screen.

---

## Author

[mahotsukai-hi](https://github.com/mahotsukai-hi)
