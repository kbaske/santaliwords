import requests
import re

def get_all_santali_pages():
    # This function finds all page titles on Santali Wikipedia
    url = "https://sat.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "aplimit": "500" # Fetch up to 500 pages at once
    }
    
    try:
        r = requests.get(url, params=params)
        pages = r.json().get('query', {}).get('allpages', [])
        return [p['title'] for p in pages]
    except:
        return []

def scrape_content():
    titles = get_all_santali_pages()
    ol_chiki_pattern = re.compile(r'[\u1C50-\u1C7F]+')
    master_words = set()
    
    # Add the titles themselves (they are usually pure Santali)
    for t in titles:
        master_words.update(ol_chiki_pattern.findall(t))
        
    # Now get the first paragraph of the top 50 pages to get real words
    for t in titles[:50]: 
        url = "https://sat.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": t,
            "format": "json"
        }
        try:
            r = requests.get(url, params=params)
            pages = r.json().get('query', {}).get('pages', {})
            for p_id in pages:
                text = pages[p_id].get('extract', '')
                master_words.update(ol_chiki_pattern.findall(text))
        except:
            continue

    if master_words:
        with open("raw_buffer.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(list(master_words)))
        print(f"Success! Found {len(master_words)} words.")
    else:
        print("Still no words found. Checking API connection...")

if __name__ == "__main__":
    scrape_content()
