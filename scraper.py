import requests
import re
import os
import json

def run_bot():
    print("🚀 Starting Santali Bot (Punctuation Filtered)...")
    
    # Updated Regex: Range 1C50-1C7F but EXCLUDING 1C7E (᱾) and 1C7F (᱿)
    # This pattern matches only actual letters.
    ol_chiki_pattern = re.compile(r'[\u1C50-\u1C7D]+')
    
    headers = {
        'User-Agent': 'SantaliWordBot/1.0 (Linguistic Research; professor@santals.in)'
    }
    
    wiki_url = "https://sat.wikipedia.org/w/api.php"
    
    # Sources: Recent changes and general search
    params_list = [
        {"action": "query", "list": "recentchanges", "rclimit": "100", "format": "json"},
        {"action": "query", "list": "search", "srsearch": "ᱥᱟᱱᱛᱟᱲᱤ", "srlimit": "100", "format": "json"}
    ]
    
    found_words = set()

    for params in params_list:
        try:
            response = requests.get(wiki_url, params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                # Process Recent Changes
                if 'recentchanges' in data.get('query', {}):
                    for item in data['query']['recentchanges']:
                        found_words.update(ol_chiki_pattern.findall(item['title']))
                
                # Process Search Results
                if 'search' in data.get('query', {}):
                    for item in data['query']['search']:
                        text_blob = item['title'] + " " + item['snippet']
                        found_words.update(ol_chiki_pattern.findall(text_blob))
            else:
                print(f"⚠️ Wikipedia Server returned status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error during fetch: {e}")

    # Handling the Wordlist
    final_file = "santali_wordlist.txt"
    existing_words = set()
    
    if os.path.exists(final_file):
        with open(final_file, "r", encoding="utf-8") as f:
            existing_words = set(line.strip() for line in f if line.strip())

    # Filter: 1. Keep only Ol Chiki letters. 2. Min length 2. 3. Strip punctuation if it slipped through.
    new_clean_words = set()
    for w in found_words:
        # Extra safety: remove punctuation characters if they are at the ends
        clean_w = w.strip('᱾᱿')
        if len(clean_w) > 1:
            new_clean_words.add(clean_w)

    all_words = sorted(list(new_clean_words | existing_words))

    if all_words:
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("\n".join(all_words))
        
        # Save count for your Hugging Face Badge
        with open("stats.json", "w") as f:
            json.dump({"word_count": len(all_words)}, f)
            
        print(f"✅ Success! Total words in database: {len(all_words)}")
    else:
        print("⚠️ No new words found. Check if Wikipedia is reachable.")

if __name__ == "__main__":
    run_bot()