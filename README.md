# TikTok OAuth CLI

A minimal CLI script that handles TikTok OAuth authorization via TikAPI and displays user session information.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your credentials**:
   Create a `.env` file with your TikAPI credentials:
   ```
   TIKAPI_KEY=your_actual_api_key_here
   TIKAPI_CLIENT_ID=your_actual_client_id_here
   ```

3. **Run the script**:
   ```bash
   python app.py
   ```

## How it 

1. **OAuth Flow**: 
   - Starts a local server on port 8000
   - Opens browser to TikAPI authorization page
   - Captures the access token from the redirect URL

2. **Session Check**:
   - Uses the access token to verify the session
   - Displays user information including:
     - User ID
     - Username
     - Email
     - Region
     - Account creation time

## Features
- OAuth authorization flow
- Local redirect handling
- Session verification
- Pretty-printed JSON output 