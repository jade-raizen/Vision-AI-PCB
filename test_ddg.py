import requests
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def test_ddg(query):
    # Try the i.js endpoint
    url = f"https://duckduckgo.com/i.js?q={query.replace(' ', '+')}&o=json"
    print(f"Testing URL: {url}")
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            try:
                data = res.json()
                results = data.get('results', [])
                print(f"Found {len(results)} results")
                if results:
                    print(f"First result: {results[0].get('image')}")
            except Exception as e:
                print(f"JSON Error: {e}")
                print(f"Response starts with: {res.text[:200]}")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_ddg("SOT-23 package")
