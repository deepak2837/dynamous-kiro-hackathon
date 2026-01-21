#!/usr/bin/env python3
"""
Simple script to view recent logs
Usage: python view_logs.py [lines] [log_file]
"""
import sys
import os
from pathlib import Path

def view_logs(lines=50, log_file="backend.log"):
    """View recent log entries"""
    log_path = Path("logs") / log_file
    
    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        return
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:]
            
        print(f"=== Last {len(recent_lines)} lines from {log_path} ===")
        for line in recent_lines:
            print(line.rstrip())
            
    except Exception as e:
        print(f"Error reading log file: {e}")

if __name__ == "__main__":
    lines = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    log_file = sys.argv[2] if len(sys.argv) > 2 else "backend.log"
    view_logs(lines, log_file)
