import re
import json
import os

def sanitize():
    ol_chiki_only = re.compile(r'[^\u1C50-\u1C7F]')
    final_file = "santali_wordlist.txt"
    
    # 1. Load current permanent list
    old_words = set()
    if os.path.exists(final_file):
        with open(final_file, "r", encoding="utf-8") as f:
            old_words = set(f.read().splitlines())

    # 2. Process newly scraped words from buffer
    if not os.path.exists("raw_buffer.txt"): return
    with open("raw_buffer.txt", "r", encoding="utf-8") as f:
        raw_data = f.read().splitlines()

    cleaned_set = set()
    for word in raw_data:
        clean = ol_chiki_only.sub('', word)
        if len(clean) > 1: # Ignore single characters
            cleaned_set.add(clean)

    # 3. Identify what is NEW today
    new_additions = list(cleaned_set - old_words)
    latest_5 = new_additions[:5] if new_additions else ["Updating..."]
    
    # 4. Save merged, sorted list
    all_words = sorted(list(cleaned_set | old_words))
    with open(final_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_words))
            
    # 5. Save metadata for Shields.io badge
    with open("stats.json", "w") as f:
        json.dump({"word_count": len(all_words)}, f)

    # 6. Update README display
    update_readme(latest_5)
    # Clear buffer
    if os.path.exists("raw_buffer.txt"): os.remove("raw_buffer.txt")

def update_readme(latest_words):
    if not os.path.exists("README.md"): return
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    list_str = "\n".join([f"- {w}" for w in latest_words])
    new_ui = f"\n### 🆕 Latest Additions\n{list_str}\n"
    content = re.sub(r".*?", new_ui, content, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    sanitize()
