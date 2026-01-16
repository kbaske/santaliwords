import re
import json
import os

def sanitize():
    # Ol Chiki Unicode range: 1C50–1C7F
    ol_chiki_pattern = re.compile(r'[\u1C50-\u1C7F]+')
    final_file = "santali_wordlist.txt"
    buffer_file = "raw_buffer.txt"
    
    # 1. Load the existing "permanent" list so we don't lose data
    old_words = set()
    if os.path.exists(final_file):
        with open(final_file, "r", encoding="utf-8") as f:
            old_words = set(line.strip() for line in f if line.strip())

    # 2. Check if the scraper actually produced any data
    if not os.path.exists(buffer_file):
        print(f"Warning: {buffer_file} not found. Scraper might have failed.")
        return

    # 3. Read and extract Ol Chiki words from the buffer
    with open(buffer_file, "r", encoding="utf-8") as f:
        raw_content = f.read()
    
    # Extract all Ol Chiki sequences
    extracted_words = ol_chiki_pattern.findall(raw_content)
    
    # Clean words: remove noise and keep only words longer than 1 character
    cleaned_set = set()
    for word in extracted_words:
        if len(word) > 1:
            cleaned_set.add(word)

    # 4. SAFETY CHECK: Only proceed if we have words to save
    # This prevents the bot from accidentally wiping the file to 0 bytes
    combined_words = cleaned_set | old_words

    if len(combined_words) > 0:
        # Sort alphabetically
        final_list = sorted(list(combined_words))
        
        # Save the updated permanent list
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_list))
            
        # Identify the newest 5 additions for the README
        new_additions = list(cleaned_set - old_words)
        latest_display = new_additions[:5] if new_additions else ["No new words added in this crawl."]
        
        # Update metadata for the Shields.io badge
        with open("stats.json", "w") as f:
            json.dump({"word_count": len(final_list)}, f)

        # Update the README UI
        update_readme(latest_display)
        
        print(f"Success! Total words in index: {len(final_list)}")
    else:
        print("Error: No Ol Chiki words were found. santali_wordlist.txt was NOT updated.")

    # 5. Clear the buffer to prepare for tomorrow
    if os.path.exists(buffer_file):
        os.remove(buffer_file)

def update_readme(latest_words):
    if not os.path.exists("README.md"):
        return
        
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    list_str = "\n".join([f"- {w}" for w in latest_words])
    new_ui = f"\n### 🆕 Latest Additions\n{list_str}\n"
    
    # Regex to swap out the old list for the new one
    updated_content = re.sub(r".*?", new_ui, content, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    sanitize()
