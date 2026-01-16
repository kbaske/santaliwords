import requests
import re

def deep_scrape():
    # Target all major Santali Wikimedia sites
    sites = ["sat.wikipedia.org", "sat.wiktionary.org", "sat.wikisource.org"]
    ol_chiki_pattern = re.compile(r'[\u1C50-\u1C7F]+')
    found_words = set()

    for site in sites:
        # Search for the most common Santali character to find all articles
        url = f"https://{site}/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": "ᱚ", 
            "srlimit": "500", # Max allowed
            "format": "json"
        }
        try:
            r = requests.get(url, params=params)
            data = r.json()
            for result in data.get('query', {}).get('search', []):
                # Scrape from Title and Snippet
                text = result['title'] + " " + result['snippet']
                found_words.update(ol_chiki_pattern.findall(text))
        except:
            continue

    with open("raw_buffer.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(list(found_words)))

if __name__ == "__main__":
    deep_scrape()
