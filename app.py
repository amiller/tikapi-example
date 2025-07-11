import os
import time
import requests
import json
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
from tikapi import TikAPI, ValidationException, ResponseException

load_dotenv()

# Configuration
REDIRECT_URL = "http://127.0.0.1:8000"
SESSION_FILE = "session.json"
access_token = None

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
                if data.get('access_token'):
                    return data['access_token']
        except:
            pass
    return None

def save_session(token):
    with open(SESSION_FILE, 'w') as f:
        json.dump({'access_token': token}, f)

class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global access_token
        # Parse the URL and get the access token
        query_components = parse_qs(urlparse(self.path).query)
        access_token = query_components.get('access_token', [None])[0]
        
        if access_token:
            save_session(access_token)
        
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
        data = response.json()
        
        if 'userInfo' in data:
            user_info = data['userInfo']
            stats = user_info.get('stats', {})
            user = user_info.get('user', {})
            
            print("\nProfile Summary:")
            print(f"Username: @{user.get('uniqueId', username)}")
            print(f"Nickname: {user.get('nickname', '')}")
            print(f"Followers: {stats.get('followerCount', 0)}")
            print(f"Following: {stats.get('followingCount', 0)}")
            print(f"Likes: {stats.get('heartCount', 0)}")
            print(f"Videos: {stats.get('videoCount', 0)}")
            if user.get('signature'):
                print(f"Bio: {user.get('signature')}")
        else:
            print("Could not find user info in response")
            
    except ValidationException as e:
        print(f"Validation error: {e} - Field: {e.field}")
    except ResponseException as e:
        print(f"Response error: {e} - Status: {e.response.status_code}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def check_notifications(api_key, account_key):
    print("\nFetching notifications...")
    api = TikAPI(api_key)
    user = api.user(accountKey=account_key)
    
    all_notifications = []
    
    try:
        response = user.notifications(count=20)
        while response:
            data = response.json()
            if 'notice_lists' in data:
                for notice_list in data['notice_lists']:
                    all_notifications.extend(notice_list.get('notice_list', []))
            
            min_time = data.get('min_time')
            max_time = data.get('max_time')
            if min_time and max_time:
                response = user.notifications(count=20, min_time=min_time, max_time=max_time)
            else:
                break

        # Save full notifications to file
        with open('mynotifs.json', 'w') as f:
            json.dump(all_notifications, f, indent=2)
        
        # Print summary
        print(f"\nFound {len(all_notifications)} notifications:")
        for notif in all_notifications:
            notif_type = notif.get('type')
            create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(notif.get('create_time', 0)))
            
            if 'digg' in notif:
                digg = notif['digg']
                if 'from_user' in digg and digg['from_user']:
                    user = digg['from_user'][0]
                    print(f"👍 Like from @{user.get('nickname')} at {create_time}")
                if 'aweme' in digg:
                    aweme = digg['aweme']
                    print(f"  📝 On post: {aweme.get('desc', '')[:100]}")
            elif 'at' in notif:
                comment = notif['at']['comment']
                content = notif['at'].get('content', '')  # Get the @mention content if present
                if 'user' in comment:
                    user = comment['user']
                    print(f"💬 Comment from @{user.get('nickname')} at {create_time}")
                    if content:
                        print(f"  @ {content}")  # Show the @mention text if present
                    print(f"  📝 {comment.get('text', '')[:100]}")
                if 'aweme' in comment:  # Use the main video info
                    aweme = comment['aweme']
                    author = aweme.get('author', {})
                    print(f"  🎥 On {author.get('nickname', '')}'s video: {aweme.get('desc', '')[:100]}")
            else:
                print(f"📢 Notification type {notif_type} at {create_time}")
                
    except ValidationException as e:
        print(f"Validation error: {e} - Field: {e.field}")
    except ResponseException as e:
        print(f"Response error: {e} - Status: {e.response.status_code}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def check_session_valid(api_key, token):
    headers = {
        'X-API-KEY': api_key,
        'X-ACCOUNT-KEY': token,
        'accept': 'application/json'
    }
    
    try:
        response = requests.get(
            'https://api.tikapi.io/user/session/check',
            headers=headers
        )
        return response.status_code == 200
    except:
        return False

def input_listener():
    global access_token
    while access_token is None and not getattr(threading.current_thread(), "stop", False):
        try:
            redirect_url = input().strip()
            if redirect_url:
                query_components = parse_qs(urlparse(redirect_url).query)
                token = query_components.get('access_token', [None])[0]
                if token:
                    access_token = token
                    save_session(token)
                    print("Access token received!")
                    return
        except:
            pass

def main():
    # Get API key and client ID from environment
    api_key = os.getenv("TIKAPI_KEY", "your_api_key_here")
    client_id = os.getenv("TIKAPI_CLIENT_ID", "your_client_id_here")
    
    if api_key == "your_api_key_here" or client_id == "your_client_id_here":
        print("Please set both TIKAPI_KEY and TIKAPI_CLIENT_ID environment variables")
        return
    
    global access_token
    access_token = load_session()
    input_thread = None
    
    # Check if we have a valid session
    if access_token and check_session_valid(api_key, access_token):
        print("Using existing session")
    else:
        try:
            # Generate authorization URL
            auth_url = f"https://tikapi.io/account/authorize?client_id={client_id}&redirect_uri={REDIRECT_URL}&scope=view_profile+explore+user.notifications"
            
            print("\nAuthorization URL (you can open this in your browser):")
            print(auth_url)
            print("\nYou can paste the redirect URL at any time, or wait for automatic browser flow...")
            
            # Start local server to handle redirect
            server_thread = threading.Thread(target=start_server)
            server_thread.daemon = True
            server_thread.start()

            # Start input listener thread
            input_thread = threading.Thread(target=input_listener)
            input_thread.daemon = True
            input_thread.start()
            
            # Try automatic browser flow
            webbrowser.open(auth_url)
            
            # Wait for either method to succeed
            while access_token is None:
                time.sleep(1)
            
        except Exception as e:
            print(f"Error during authorization: {e}")
            return
        finally:
            if input_thread and input_thread.is_alive():
                setattr(input_thread, "stop", True)
                input_thread.join(timeout=1)
    
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
        
        # Then check notifications
        check_notifications(api_key, access_token)
    else:
        print(f"Failed to get session info: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    main()
