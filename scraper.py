import requests
import re
import os
import json

def run_bot():
    print("🚀 Starting Santali Bot...")
    # Unicode for Ol Chiki
    ol_chiki_pattern = re.compile(r'[\u1C50-\u1C7F]+')
    
    # 1. Fetch recent active titles from Santali Wikipedia
    wiki_url = "https://sat.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "recentchanges",
        "rclimit": "100",
        "format": "json"
    }
    
    found_words = set()
    
    try:
        response = requests.get(wiki_url, params=params, timeout=15)
        rc_data = response.json().get('query', {}).get('recentchanges', [])
        titles = [item['title'] for item in rc_data]
        print(f"Found {len(titles)} active pages to check.")
        
        # 2. Scrape words from these titles and their full text
        for title in titles:
            # Find words in the title itself
            found_words.update(ol_chiki_pattern.findall(title))
            
            # Fetch content of the page
            content_params = {
                "action": "query",
                "prop": "extracts",
                "explaintext": True,
                "titles": title,
                "format": "json"
            }
            content_resp = requests.get(wiki_url, params=content_params, timeout=15)
            pages = content_resp.json().get('query', {}).get('pages', {})
            for p_id in pages:
                text = pages[p_id].get('extract', '')
                if text:
                    found_words.update(ol_chiki_pattern.findall(text))
    
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 3. Handle Saving
    final_file = "santali_wordlist.txt"
    
    # Load existing
    existing_words = set()
    if os.path.exists(final_file):
        with open(final_file, "r", encoding="utf-8") as f:
            existing_words = set(line.strip() for line in f if line.strip())

    # Merge and Clean (ignore single letters like ᱚ)
    new_clean_words = {w for w in found_words if len(w) > 1}
    all_words = sorted(list(new_clean_words | existing_words))

    if len(all_words) > 0:
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("\n".join(all_words))
        
        with open("stats.json", "w") as f:
            json.dump({"word_count": len(all_words)}, f)
            
        print(f"✅ Success! Total words in database: {len(all_words)}")
    else:
        print("⚠️ No Ol Chiki words found in the last 100 changes.")

if __name__ == "__main__":
    run_bot()
