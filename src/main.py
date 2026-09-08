import os
import sys
import json

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_pipeline import run_rag_pipeline

def main():
    print("=" * 65)
    print("  [RAG App] SchemeAssist - End-to-End RAG Pipeline Run")
    print("=" * 65)
    
    test_query = "welfare schemes eligibility guidance and income limits"
    result = run_rag_pipeline(test_query, top_k=3)
    
    print("\n--- [FINAL GENERATED RAG ANSWER] ---")
    print(result["answer"])
    
    print("\n--- [RETURNED SOURCES] ---")
    for src in result["sources"]:
        print(f"[{src['citation_index']}] {src['source']} (Section: {src['section']}, Page: {src['page']})")
    
    print("\n=" + "=" * 64)
    print("  [SUCCESS] END-TO-END RAG PIPELINE EXECUTED PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    main()
