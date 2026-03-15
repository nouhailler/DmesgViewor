#!/usr/bin/env python3
"""DMESGVIEWOR – Graphical kernel log viewer for Debian Linux.

Usage:
    python3 main.py
"""
import sys
import os

# Ensure the project root is on sys.path so all imports work regardless
# of where the script is invoked from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import run

if __name__ == "__main__":
    run()
