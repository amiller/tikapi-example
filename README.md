# TikAPI Client

A simple Python client for interacting with TikTok's API via [TikAPI.io](https://tikapi.io/). This tool allows you to:
- View public profile information
- Check notifications
- Save notifications to a JSON file for later analysis

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment:
- Copy `.env.example` to `.env`
- Get your API key and client ID from [TikAPI Dashboard](https://tikapi.io/dashboard)
- Add them to your `.env` file:
  ```
  TIKAPI_KEY=your_api_key_here
  TIKAPI_CLIENT_ID=your_client_id_here
  ```

## Usage

Run the script:
```bash
python app.py
```

On first run, the script will:
1. Open your browser to authorize with TikTok
2. Save the session for future use
3. Display your profile information
4. Fetch and save your notifications to `mynotifs.json`

The script will reuse your saved session on subsequent runs.

## Output Files

- `session.json`: Stores your session token
- `mynotifs.json`: Contains your full notification data
- `.env`: Your API credentials (not tracked in git)

## Notes

- All sensitive files (`.env`, `session.json`, etc.) are git-ignored by default
- The script uses a local server on port 8000 for the OAuth flow
- You can manually paste the redirect URL if the automatic browser flow fails 