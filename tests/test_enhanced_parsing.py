#!/usr/bin/env python3
"""
Test script to verify enhanced parsing functionality with regex fallback
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repomap_class import RepoMap
from utils import read_text

def test_parsing():
    """Test parsing of Ecne-AI-Report-Builder files"""
    
    # Test with the problematic project
    project_root = "/home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder"
    
    # Initialize RepoMap with debug output
    repo_map = RepoMap(
        verbose=True,
        output_handler_funcs={
            'info': print,
            'warning': print,
            'error': print,
            'debug': print
        }
    )
    
    # Test specific files
    test_files = [
        os.path.join(project_root, "app.py"),
        os.path.join(project_root, "report_builder.py")
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n=== Testing {file_path} ===")
            rel_path = os.path.relpath(file_path, project_root)
            
            # Test parsing
            tags = repo_map.get_tags_raw(file_path, rel_path)
            print(f"Found {len(tags)} tags in {rel_path}")
            
            for tag in tags[:10]:  # Show first 10 tags
                print(f"  {tag.kind}: {tag.name} (line {tag.line})")
                
            if len(tags) > 10:
                print(f"  ... and {len(tags) - 10} more tags")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    test_parsing()