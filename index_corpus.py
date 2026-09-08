import os
import sys

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.indexing import run_indexing_pipeline

if __name__ == "__main__":
    run_indexing_pipeline("data")
