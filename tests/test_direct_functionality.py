#!/usr/bin/env python3
"""
Test the core functionality directly without MCP wrapper
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repomap_server import find_src_files, parse_gitignore, should_exclude_from_gitignore, is_source_file
from repomap_class import RepoMap

def test_core_functionality():
    """Test the core functionality that powers the MCP tools"""
    print("=== Testing Core RepoMapper Functionality ===")
    target_dir = "/home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder"
    print(f"Target: {target_dir}")
    print()
    
    # Test 1: File filtering with .gitignore
    print("1. Testing file filtering with .gitignore...")
    files = find_src_files(
        target_dir,
        file_patterns=[".py", ".js", ".java", ".rb"]
    )
    print(f"   Found {len(files)} source files")
    print(f"   Sample files: {files[:5]}")
    print()
    
    # Debug: Test the find_src_files function step by step
    print("1d. Debugging find_src_files step by step...")
    test_dir = target_dir
    if not os.path.isdir(test_dir):
        print(f"   {test_dir} is not a directory")
    else:
        # Test the extension matching logic
        extensions = {".py", ".js", ".java", ".rb"}
        print(f"   Looking for extensions: {extensions}")
        
        # Test directory walking manually
        found_files = []
        for root, dirs, files in os.walk(test_dir):
            print(f"   Walking: {root}")
            print(f"     Directories: {dirs[:3]}{'...' if len(dirs) > 3 else ''}")
            print(f"     Files: {files[:3]}{'...' if len(files) > 3 else ''}")
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in extensions:
                        found_files.append(file_path)
                        if len(found_files) <= 3:
                            print(f"     Found: {file_path}")
        
        print(f"   Manually found {len(found_files)} files with target extensions")
        if found_files:
            print(f"   Sample: {found_files[:3]}")
    print()
    
    # Test 1b: Test without .gitignore filtering to see what's available
    print("1b. Testing without .gitignore filtering...")
    import fnmatch
    all_py_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if fnmatch.fnmatch(file, "*.py"):
                all_py_files.append(os.path.join(root, file))
    print(f"   Found {len(all_py_files)} Python files total")
    print(f"   Sample: {all_py_files[:5]}")
    print()
    
    # Test 1c: Test specific source files manually
    print("1c. Testing specific source files manually...")
    test_files = [
        os.path.join(target_dir, "report_builder.py"),
        os.path.join(target_dir, "app.py")
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"   Testing {os.path.basename(test_file)}...")
            # Check if it would be excluded by .gitignore
            gitignore_patterns = parse_gitignore(target_dir)
            excluded = should_exclude_from_gitignore(test_file, gitignore_patterns, target_dir)
            print(f"      Excluded by .gitignore: {excluded}")
            
            # Check if it's a source file
            is_source = is_source_file(test_file, [".py"])
            print(f"      Is source file: {is_source}")
        else:
            print(f"   {os.path.basename(test_file)}: File not found")
    print()
    
    # Test 1e: Test .gitignore pattern matching specifically for host_venv
    print("1e. Testing host_venv pattern matching...")
    gitignore_patterns = parse_gitignore(target_dir)
    print(f"   .gitignore patterns: {gitignore_patterns}")
    
    # Test host_venv directory specifically
    host_venv_path = os.path.join(target_dir, "host_venv")
    if os.path.exists(host_venv_path):
        print(f"   Testing host_venv directory: {host_venv_path}")
        excluded = should_exclude_from_gitignore(host_venv_path, gitignore_patterns, target_dir)
        print(f"      Excluded by .gitignore: {excluded}")
        
        # Test a file inside host_venv
        test_venv_file = os.path.join(host_venv_path, "lib", "python3.13", "site-packages", "six.py")
        if os.path.exists(test_venv_file):
            excluded_file = should_exclude_from_gitignore(test_venv_file, gitignore_patterns, target_dir)
            print(f"      Testing {os.path.basename(test_venv_file)}: Excluded: {excluded_file}")
    print()
    
    # Test 2: .gitignore parsing
    print("2. Testing .gitignore parsing...")
    gitignore_patterns = parse_gitignore(target_dir)
    print(f"   Found {len(gitignore_patterns)} patterns: {gitignore_patterns}")
    print()
    
    # Test 3: RepoMap parsing
    print("3. Testing RepoMap parsing...")
    repomap = RepoMap()
    
    # Test on a few key files
    test_files = [f for f in files if 'app.py' in f or 'report_builder.py' in f][:2]
    
    for file_path in test_files:
        print(f"   Parsing {os.path.basename(file_path)}...")
        try:
            tags = repomap.get_tags_raw(file_path)
            print(f"      Found {len(tags)} tags")
            definitions = [t for t in tags if t['type'] == 'definition']
            references = [t for t in tags if t['type'] == 'reference']
            print(f"      -> {len(definitions)} definitions, {len(references)} references")
        except Exception as e:
            print(f"      Error: {e}")
    print()
    
    print("✅ Core functionality test completed successfully!")
    return files

if __name__ == "__main__":
    test_core_functionality()