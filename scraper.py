import requests
import re
import os
import json

def run_bot():
    print("🚀 Starting Santali Bot (Strict Punctuation Filtering)...")
    
    # Updated Regex: Range 1C50-1C7D 
    # This specifically stops before 1C7E (᱾) and 1C7F (᱿)
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
                
                # Extract from Recent Changes
                if 'recentchanges' in data.get('query', {}):
                    for item in data['query']['recentchanges']:
                        # Extract and immediately clean
                        raw_found = ol_chiki_pattern.findall(item['title'])
                        for word in raw_found:
                            # .strip() removes characters from BOTH beginning and end
                            found_words.add(word.strip('᱾᱿'))
                
                # Extract from Search Results
                if 'search' in data.get('query', {}):
                    for item in data['query']['search']:
                        text_blob = item['title'] + " " + item['snippet']
                        raw_found = ol_chiki_pattern.findall(text_blob)
                        for word in raw_found:
                            found_words.add(word.strip('᱾᱿'))
            else:
                print(f"⚠️ Server status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error during fetch: {e}")

    # Handling the Wordlist
    final_file = "santali_wordlist.txt"
    existing_words = set()
    
    if os.path.exists(final_file):
        with open(final_file, "r", encoding="utf-8") as f:
            existing_words = set(line.strip() for line in f if line.strip())

    # Final Filter: Min length 2 and ensure no punctuation exists
    new_clean_words = set()
    for w in found_words:
        clean_w = w.strip('᱾᱿')
        if len(clean_w) > 1:
            new_clean_words.add(clean_w)

    all_words = sorted(list(new_clean_words | existing_words))

    if all_words:
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("\n".join(all_words))
        
        with open("stats.json", "w") as f:
            json.dump({"word_count": len(all_words)}, f)
            
        print(f"✅ Success! Total words: {len(all_words)}")
    else:
        print("⚠️ No words found yet. Run the Action manually to test.")

if __name__ == "__main__":
    run_bot()