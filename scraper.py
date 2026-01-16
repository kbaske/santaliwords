import requests
import re
import os
import json

def run_bot():
    print("🚀 Starting Santali Bot with Headers...")
    
    # Unicode for Ol Chiki
    ol_chiki_pattern = re.compile(r'[\u1C50-\u1C7F]+')
    
    # Wikipedia prefers a User-Agent that describes your bot
    headers = {
        'User-Agent': 'SantaliWordBot/1.0 (https://github.com/YOUR_USERNAME; contact@example.com)'
    }
    
    wiki_url = "https://sat.wikipedia.org/w/api.php"
    
    # Try multiple sources: Recent Changes AND a Search for common words
    params_list = [
        {"action": "query", "list": "recentchanges", "rclimit": "50", "format": "json"},
        {"action": "query", "list": "search", "srsearch": "ᱥᱟᱱᱛᱟᱲᱤ", "srlimit": "50", "format": "json"}
    ]
    
    found_words = set()

    for params in params_list:
        try:
            response = requests.get(wiki_url, params=params, headers=headers, timeout=15)
            # Check if we actually got JSON
            if response.status_code == 200:
                data = response.json()
                
                # Extract from recent changes
                if 'recentchanges' in data.get('query', {}):
                    for item in data['query']['recentchanges']:
                        found_words.update(ol_chiki_pattern.findall(item['title']))
                
                # Extract from search results
                if 'search' in data.get('query', {}):
                    for item in data['query']['search']:
                        found_words.update(ol_chiki_pattern.findall(item['title'] + " " + item['snippet']))
            else:
                print(f"⚠️ Server returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Connection Error during fetch: {e}")

    # Handle Saving
    final_file = "santali_wordlist.txt"
    existing_words = set()
    
    if os.path.exists(final_file):
        with open(final_file, "r", encoding="utf-8") as f:
            existing_words = set(line.strip() for line in f if line.strip())

    new_clean_words = {w for w in found_words if len(w) > 1}
    all_words = sorted(list(new_clean_words | existing_words))

    if all_words:
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("\n".join(all_words))
        
        with open("stats.json", "w") as f:
            json.dump({"word_count": len(all_words)}, f)
            
        print(f"✅ Success! Total words in database: {len(all_words)}")
    else:
        print("⚠️ No words found. Ensure Wikipedia has active Ol Chiki content.")

if __name__ == "__main__":
    run_bot()