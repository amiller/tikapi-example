import os
import time
import requests
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
import json
from tikapi import TikAPI, ValidationException, ResponseException

load_dotenv()

# Configuration
REDIRECT_URL = "http://127.0.0.1:8000"
access_token = None

class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global access_token
        # Parse the URL and get the access token
        query_components = parse_qs(urlparse(self.path).query)
        access_token = query_components.get('access_token', [None])[0]
        
        # Send a simple response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Authorization successful! You can close this window.")
        
        # Stop the server
        threading.Thread(target=self.server.shutdown).start()

def start_server():
    server = HTTPServer(('127.0.0.1', 8000), TokenHandler)
    server.serve_forever()

def check_public_profile(api_key, username):
    print(f"\nFetching public profile for @{username}...")
    api = TikAPI(api_key)
    
    try:
        response = api.public.check(username=username)
        print("\nPublic Profile Info:")
        print(json.dumps(response.json(), indent=2))
    except ValidationException as e:
        print(f"Validation error: {e} - Field: {e.field}")
    except ResponseException as e:
        print(f"Response error: {e} - Status: {e.response.status_code}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    # Get API key and client ID from environment
    api_key = os.getenv("TIKAPI_KEY", "your_api_key_here")
    client_id = os.getenv("TIKAPI_CLIENT_ID", "your_client_id_here")
    
    if api_key == "your_api_key_here" or client_id == "your_client_id_here":
        print("Please set both TIKAPI_KEY and TIKAPI_CLIENT_ID environment variables")
        return
    
    try:
        # Start local server to handle redirect
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Generate authorization URL using the format from documentation
        auth_url = f"https://tikapi.io/account/authorize?client_id={client_id}&redirect_uri={REDIRECT_URL}&scope=view_profile+explore"
        
        print(f"\nOpening authorization URL in your browser...")
        webbrowser.open(auth_url)
        print("Waiting for authorization...")
        
        # Wait for the access token
        while access_token is None:
            time.sleep(1)
        
        print("\nAccess token received!")
        
        # Make request to session check endpoint
        print("\nFetching user session info...")
        headers = {
            'X-API-KEY': api_key,
            'X-ACCOUNT-KEY': access_token,
            'accept': 'application/json'
        }
        
        response = requests.get(
            'https://api.tikapi.io/user/session/check',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\nUser Session Info:")
            print(json.dumps(data, indent=2))
            
            # After successful auth, check a public profile
            check_public_profile(api_key, data['data']['username'])
        else:
            print(f"Failed to get session info: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
