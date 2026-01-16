import requests
import re
import os
import json
import time

def run_deep_scrape():
    print("🚀 Starting Deep Crawl for Santali Words...")
    
    # Strictly Ol Chiki letters (excludes punctuation ᱾ and ᱿)
    ol_chiki_pattern = re.compile(r'[\u1C50-\u1C7D]+')
    headers = {'User-Agent': 'SantaliDeepBot/1.0 (Linguistic Research; professor@santals.in)'}
    wiki_url = "https://sat.wikipedia.org/w/api.php"
    
    found_words = set()

    # 1. Get all page titles (up to 500 per request)
    print("📋 Fetching article index...")
    list_params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "aplimit": "500" 
    }
    
    try:
        r = requests.get(wiki_url, params=list_params, headers=headers)
        pages = r.json().get('query', {}).get('allpages', [])
        titles = [p['title'] for p in pages]
        print(f"✅ Found {len(titles)} pages. Starting deep text extraction...")

        # 2. Fetch full text for these pages in batches of 50
        for i in range(0, len(titles), 50):
            batch = titles[i:i+50]
            print(f"📖 Scraping batch {i//50 + 1}...")
            
            content_params = {
                "action": "query",
                "prop": "extracts",
                "explaintext": True,
                "titles": "|".join(batch),
                "format": "json"
            }
            
            res = requests.get(wiki_url, params=content_params, headers=headers)
            page_data = res.json().get('query', {}).get('pages', {})
            
            for p_id in page_data:
                text = page_data[p_id].get('extract', '')
                if text:
                    # Extract and clean every word
                    raw_extracted = ol_chiki_pattern.findall(text)
                    for word in raw_extracted:
                        clean_word = word.strip('᱾᱿')
                        if len(clean_word) > 1:
                            found_words.add(clean_word)
            
            # Small delay to be polite to Wikipedia servers
            time.sleep(1)

    except Exception as e:
        print(f"❌ Error: {e}")

    # 3. Merge with existing wordlist
    final_file = "santali_wordlist.txt"
    existing_words = set()
    if os.path.exists(final_file):
        with open(final_file, "r", encoding="utf-8") as f:
            existing_words = set(line.strip() for line in f if line.strip())

    all_words = sorted(list(found_words | existing_words))

    # 4. Save results
    if all_words:
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("\n".join(all_words))
        
        with open("stats.json", "w") as f:
            json.dump({"word_count": len(all_words)}, f)
            
        print(f"🎉 Success! Database now contains {len(all_words)} unique words.")
    else:
        print("⚠️ No words extracted. Verify Wikipedia connectivity.")

if __name__ == "__main__":
    run_deep_scrape()