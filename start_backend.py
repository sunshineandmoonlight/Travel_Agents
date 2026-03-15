#!/usr/bin/env python
"""Simple backend startup script"""
import sys
import os

# Fix I/O issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    # 旅行系统入口
    uvicorn.run("app.travel_main:app", host="0.0.0.0", port=8006, log_level="info")
