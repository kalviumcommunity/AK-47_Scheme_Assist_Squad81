# -*- coding: utf-8 -*-
"""
api/main.py - SchemeAssist API Entry Point & Launcher
Re-exports the canonical FastAPI application from src.api.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.api import app, start

__all__ = ["app"]

if __name__ == "__main__":
    start()