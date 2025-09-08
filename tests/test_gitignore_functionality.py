#!/usr/bin/env python3
"""
Test script to verify .gitignore functionality is working
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repomap_server import find_src_files, parse_gitignore, should_exclude_from_gitignore

def test_gitignore_functionality():
    """Test that .gitignore patterns are properly handled"""
    
    print("=== Testing .gitignore Functionality ===")
    
    # Test 1: Parse .gitignore patterns
    print("\n1. Testing .gitignore pattern parsing...")
    patterns = parse_gitignore(".")
    print(f"Found {len(patterns)} patterns in .gitignore: {patterns}")
    
    # Test 2: Test pattern matching
    print("\n2. Testing pattern matching...")
    test_files = [
        "/home/dundell2/Desktop/dev/repomap/RepoMapper/.aider_test",
        "/home/dundell2/Desktop/dev/repomap/RepoMapper/.repomap_cache",
        "/home/dundell2/Desktop/dev/repomap/RepoMapper/venv/bin/python",
        "/home/dundell2/Desktop/dev/repomap/RepoMapper/__pycache__/test.pyc",
        "/home/dundell2/Desktop/dev/repomap/RepoMapper/normal_file.py"
    ]
    
    for file_path in test_files:
        should_exclude = should_exclude_from_gitignore(file_path, patterns, "/home/dundell2/Desktop/dev/repomap/RepoMapper")
        status = "EXCLUDE" if should_exclude else "INCLUDE"
        print(f"  {status}: {os.path.basename(file_path)}")
    
    # Test 3: Test file filtering with .gitignore
    print("\n3. Testing file filtering with .gitignore...")
    files = find_src_files(".", [".py"])
    print(f"Found {len(files)} Python files after .gitignore filtering")
    
    # Show some files to verify filtering is working
    if files:
        print("Sample files found:")
        for file in files[:5]:
            print(f"  - {file}")
    
    print("\n✅ .gitignore functionality test completed!")

if __name__ == "__main__":
    test_gitignore_functionality()