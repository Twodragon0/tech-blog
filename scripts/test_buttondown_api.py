#!/usr/bin/env python3
"""
Test Buttondown API connection and authentication.
This script helps verify that the API key is working correctly.
"""

import os
import sys
import requests
from pathlib import Path

# Load environment variables from .env file
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / '.env'

if ENV_FILE.exists():
    with open(ENV_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()


def test_api_connection(api_key: str) -> bool:
    """Test Buttondown API connection and authentication."""
    # Test endpoint: Get subscribers list (read-only, safe to test)
    url = "https://api.buttondown.com/v1/subscribers"
    
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔍 Testing Buttondown API connection...")
        print(f"   Endpoint: {url}")
        # Security: Mask API key in logs - only show first 4 and last 4 characters
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
        print(f"   API Key: {masked_key}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"✅ API connection successful!")
            print(f"   Subscribers: {count}")
            return True
        elif response.status_code == 401:
            print(f"❌ Authentication failed (401 Unauthorized)")
            print(f"   Please check your BUTTONDOWN_API_KEY")
            print(f"   Make sure the API key is correct and has proper permissions")
            return False
        elif response.status_code == 404:
            print(f"❌ Resource not found (404)")
            print(f"   This might indicate an invalid API endpoint")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout: API did not respond within 10 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print(f"   Please check your internet connection")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False


def main():
    api_key = os.environ.get('BUTTONDOWN_API_KEY')
    
    if not api_key:
        print("❌ BUTTONDOWN_API_KEY environment variable not set")
        print("   Set it in .env file or export it:")
        print("   export BUTTONDOWN_API_KEY='your-api-key'")
        sys.exit(1)
    
    success = test_api_connection(api_key)
    
    if success:
        print("\n✅ API test passed! You can now use Buttondown API.")
        sys.exit(0)
    else:
        print("\n❌ API test failed. Please check your API key and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
