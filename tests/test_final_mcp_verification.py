#!/usr/bin/env python3
"""
Final verification test for MCP functionality.
Tests the core repo_map functionality directly without MCP server overhead.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repomap_server import repo_map, search_identifiers

def test_repo_map_functionality():
    """Test the repo_map function directly"""
    print("=== Testing repo_map Function Directly ===")
    print(f"Target: /home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder")
    
    try:
        # Test with file patterns and scan directories
        result = repo_map(
            project_root="/home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder",
            file_patterns=['.py'],
            scan_directories=['/home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder'],
            token_limit=4096,
            verbose=True
        )
        
        print(f"✅ repo_map executed successfully!")
        print(f"Result type: {type(result)}")
        
        if isinstance(result, dict):
            if 'map' in result:
                print(f"Generated map length: {len(result['map'])} characters")
                print(f"Map preview: {result['map'][:200]}...")
            
            if 'report' in result:
                report = result['report']
                print(f"Files included: {len(report.get('included', []))}")
                print(f"Files excluded: {len(report.get('excluded', {}))}")
                print(f"Definition matches: {report.get('definition_matches', 0)}")
                print(f"Reference matches: {report.get('reference_matches', 0)}")
                print(f"Total files considered: {report.get('total_files_considered', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ repo_map failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_identifiers_functionality():
    """Test the search_identifiers function directly"""
    print("\n=== Testing search_identifiers Function Directly ===")
    
    try:
        result = search_identifiers(
            project_root="/home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder",
            query="ReportBuilder",
            max_results=10,
            context_lines=2
        )
        
        print(f"✅ search_identifiers executed successfully!")
        print(f"Result type: {type(result)}")
        
        if isinstance(result, dict) and 'results' in result:
            print(f"Found {len(result['results'])} results for 'ReportBuilder'")
            for i, res in enumerate(result['results'][:3]):
                print(f"  {i+1}. {res.get('file', 'N/A')}:{res.get('line', 'N/A')} - {res.get('context', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ search_identifiers failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Final MCP Functionality Verification")
    print("=" * 50)
    
    success1 = test_repo_map_functionality()
    success2 = test_search_identifiers_functionality()
    
    if success1 and success2:
        print("\n🎉 All MCP functionality tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())