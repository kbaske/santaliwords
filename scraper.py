import requests
import re
import os

def collect_words():
    # Targets: Santali Wikipedia, Wiktionary, and Wikisource
    sources = ["sat.wikipedia.org", "sat.wiktionary.org", "sat.wikisource.org"]
    ol_chiki_pattern = re.compile(r'[\u1C50-\u1C7F]+')
    master_words = set()

    # Broad search queries to find many pages
    queries = ["ᱟ", "ᱮ", "ᱤ", "ᱩ", "ᱳ", "ᱴ", "ᱞ", "ᱠ"]

    for site in sources:
        for q in queries:
            url = f"https://{site}/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": q,
                "srlimit": "300"
            }
            try:
                r = requests.get(url, params=params, timeout=10)
                data = r.json()
                for res in data.get('query', {}).get('search', []):
                    words = ol_chiki_pattern.findall(res['title'] + " " + res['snippet'])
                    master_words.update(words)
            except Exception as e:
                print(f"Error on {site}: {e}")

    # Append new words to the existing temporary file
    with open("raw_buffer.txt", "a", encoding="utf-8") as f:
        f.write("\n".join(list(master_words)) + "\n")

if __name__ == "__main__":
    collect_words()
