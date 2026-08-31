import os
import sys

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cleaning import clean_text

def run_comparative_verification():
    print("=" * 75)
    print("  [CLEANER TEST] Text Extraction Cleaning Pipeline Comparative Report")
    print("=" * 75)
    
    data_dir = "data"
    test_files = ["sample_text.txt", "sample_html.html"]
    
    for filename in test_files:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(f"[ERROR] Test file {filepath} not found!")
            continue
            
        print(f"\n--- FILE: {filename} ---")
        
        # 1. Read Raw Content
        with open(filepath, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
        # If HTML, extract raw text first (matching ingestion) so that the comparison
        # is raw extracted text vs cleaned text.
        if filename.endswith((".html", ".htm")):
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(raw_content, "html.parser")
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            raw_extracted = soup.get_text(separator=" ").strip()
        else:
            raw_extracted = raw_content

        print(">>> BEFORE (RAW EXTRACTED TEXT):")
        print("-" * 50)
        raw_preview = raw_extracted[:600]
        print(raw_preview)
        if len(raw_extracted) > 600:
            print("... [TRUNCATED] ...")
        print("-" * 50)
        
        # 2. Apply Custom Cleaning
        cleaned_content = clean_text(raw_extracted)
        
        print("\n>>> AFTER (CLEANED RAG-READY TEXT):")
        print("-" * 50)
        print(cleaned_content)
        print("-" * 50)
        
        # Print comparison statistics
        print(f"Statistics: Raw characters: {len(raw_extracted)} | Cleaned characters: {len(cleaned_content)}")
        reduction = ((len(raw_extracted) - len(cleaned_content)) / len(raw_extracted)) * 100 if len(raw_extracted) > 0 else 0
        print(f"Noise reduction: {reduction:.2f}%")

        
    print("\n" + "=" * 75)
    print("  [SUCCESS] Comparative Verification Completed Successfully!")
    print("=" * 75)

if __name__ == "__main__":
    run_comparative_verification()
