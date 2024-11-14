import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
LINKEDIN_USER_ID = os.getenv("LINKEDIN_USER_ID")

# LinkedIn headers for API calls
linkedin_headers = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Slack headers for API calls
slack_headers = {
    "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    "Content-Type": "application/json"
}

def get_recent_linkedin_posts():
    """
    Fetches recent LinkedIn posts for the user.
    """
    url = f"https://api.linkedin.com/v2/activityFeeds?q=authors&authors=List({LINKEDIN_USER_ID})"
    response = requests.get(url, headers=linkedin_headers)
    
    if response.status_code == 200:
        posts = response.json().get("elements", [])
        return posts
    else:
        print(f"Error fetching LinkedIn posts: {response.status_code}")
        print(response.json())
        return []

def send_slack_notification(message):
    """
    Sends a notification to a Slack channel.
    """
    url = "https://slack.com/api/chat.postMessage"
    payload = {
        "channel": SLACK_CHANNEL_ID,
        "text": message
    }
    
    response = requests.post(url, headers=slack_headers, json=payload)
    
    if response.status_code == 200 and response.json().get("ok"):
        print("Notification sent to Slack.")
    else:
        print("Failed to send Slack notification.")
        print(response.json())

def main():
    # Store seen post IDs to avoid duplicate notifications
    seen_posts = set()

    while True:
        print("Checking for new LinkedIn posts...")
        posts = get_recent_linkedin_posts()
        
        for post in posts:
            post_id = post.get("id")
            if post_id not in seen_posts:
                content = post.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {}).get("shareCommentary", {}).get("text", "")
                message = f"New LinkedIn Post: {content}"
                send_slack_notification(message)
                seen_posts.add(post_id)
        
        # Check every 5 minutes
        time.sleep(300)

if __name__ == "__main__":
    main()
