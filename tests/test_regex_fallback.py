#!/usr/bin/env python3
"""
Test the regex fallback functionality specifically.
"""

import sys
import os
import re

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repomap_class import RepoMap
from utils import read_text
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)-5s %(message)s')
log = logging.getLogger(__name__)

def test_regex_patterns():
    """Test regex patterns on sample code"""
    print("=== Testing Regex Patterns ===")
    
    # Sample code from report_builder.py
    sample_code = """
import os
import datetime
import time
import re
import traceback
import random

from functions.config import load_config
from functions.args import parse_arguments

def main():
    \"\"\"Main function to orchestrate the AI report generation workflow.\"\"\"
    print("--- Starting AI Report Generator (Refactored) ---")
    start_time = time.time()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    env_config, models_config = load_config(script_dir)
    args = parse_arguments(models_config)
    
    final_model_key = "default_model"
    env_model_key = os.getenv("DEFAULT_MODEL_CONFIG")
    
    if args.llm_model:
        final_model_key = args.llm_model
        print(f"Using LLM model specified via command line: '{final_model_key}'")
        env_config['final_model_key'] = final_model_key
        log_to_file(f"Model Selection: Using command line override: '{final_model_key}'")
    elif env_model_key:
        final_model_key = env_model_key
        print(f"Using LLM model specified via .env: '{final_model_key}'")
        env_config['final_model_key'] = final_model_key
        log_to_file(f"Model Selection: Using .env setting: '{final_model_key}'")
    else:
        print(f"Using default LLM model: '{final_model_key}'")
        env_config['final_model_key'] = final_model_key
        log_to_file(f"Model Selection: Using default: '{final_model_key}'")
    
    final_model_config = models_config.get(final_model_key)
    if not final_model_config or not isinstance(final_model_config, dict):
        print(f"Error: Final selected model key '{final_model_key}' configuration not found")
        exit(1)
    if 'model' not in final_model_config:
        print(f"Error: 'model' name is missing in the configuration for '{final_model_key}'")
        exit(1)
    
    env_config["selected_model_config"] = final_model_config
    log_to_file(f"Final Model Config Used: {final_model_config}")
    
    archive_base_dir = os.path.join(script_dir, "archive")
    topic_slug = re.sub(r'\W+', '_', args.topic)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_archive_dir_name = f"{timestamp}_{topic_slug}"
    run_archive_dir_path = os.path.join(archive_base_dir, run_archive_dir_name)
    
    set_run_archive_dir(run_archive_dir_path)
    
    try:
        os.makedirs(run_archive_dir_path, exist_ok=True)
        print(f"Created archive directory: {run_archive_dir_path}")
        log_to_file(f"--- AI Report Generator Run Start ({timestamp}) ---")
        log_to_file(f"Run CWD: {os.getcwd()}")
        log_to_file(f"Args: {vars(args)}")
    except OSError as e:
        print(f"Error creating archive directory {run_archive_dir_path}: {e}")
        set_run_archive_dir(None)
        log_to_file("Error: Failed to create archive directory. Archiving disabled for this run.")
    
    try:
        reference_docs_content = load_reference_documents(args)
        if not reference_docs_content and (args.reference_docs or args.reference_docs_folder):
             print("Warning: No valid reference documents were loaded from specified paths or folder.")
             log_to_file("Warning: Reference docs/folder specified, but no content loaded.")
    """
    
    # Test the regex patterns manually
    patterns = [
        (r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "def", 1),
        (r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(|:)', "def", 1),
        (r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?!\d)', "def", 1),
        (r'^\s*(?:from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import|import\s+([a-zA-Z_][a-zA-Z0-9_.]*))', "ref", 1),
        (r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "ref", 1),
    ]
    
    print("Testing regex patterns on sample code:")
    print("-" * 50)
    
    tags = []
    for i, line in enumerate(sample_code.splitlines()):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        for pattern, kind, group_num in patterns:
            match = re.search(pattern, line)
            if match:
                # Extract the identifier name from the appropriate capture group
                name = None
                for g in range(1, match.lastindex + 1 if match.lastindex else 1):
                    candidate = match.group(g)
                    if candidate and candidate not in ['from', 'import']:  # Skip keywords
                        name = candidate
                        break
                
                if name:
                    print(f"Line {i+1}: {kind.upper()} - {name}")
                    print(f"  Pattern: {pattern}")
                    print(f"  Line: {line}")
                    print()
                    tags.append((i+1, name, kind))
                    break  # Only match one pattern per line
    
    print(f"Total tags found: {len(tags)}")
    return len(tags) > 0

def test_repo_map_regex():
    """Test RepoMap regex fallback directly"""
    print("\n=== Testing RepoMap Regex Fallback ===")
    
    try:
        # Initialize RepoMap
        repo_mapper = RepoMap(
            map_tokens=2048,
            root="/home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder",
            file_reader_func=read_text,
            output_handler_funcs={'info': print, 'warning': print, 'error': print, 'debug': print},
            verbose=True,
            exclude_unranked=False
        )
        
        # Test file
        test_file = "/home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder/report_builder.py"
        rel_fname = os.path.relpath(test_file, "/home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder")
        
        print(f"Testing regex fallback on: {rel_fname}")
        
        # Read the file content
        code = read_text(test_file)
        if not code:
            print("Failed to read file content")
            return False
        
        # Test regex fallback directly
        tags = repo_mapper._regex_fallback(code, rel_fname, test_file, 'python')
        print(f"Regex fallback found {len(tags)} tags")
        
        if tags:
            print("Sample tags:")
            for tag in tags[:10]:
                print(f"  {tag.kind}: {tag.name} (line {tag.line})")
        
        return len(tags) > 0
        
    except Exception as e:
        print(f"Error testing regex fallback: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Regex Fallback Testing")
    print("=" * 50)
    
    success1 = test_regex_patterns()
    success2 = test_repo_map_regex()
    
    if success1 and success2:
        print("\n🎉 Regex fallback tests passed!")
        return 0
    else:
        print("\n❌ Some regex fallback tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())