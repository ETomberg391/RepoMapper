#!/usr/bin/env python3
"""
Direct simulation of MCP repo_map functionality for testing
without requiring MCP connection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repomap_server import repo_map

def test_mcp_simulation():
    """Simulate the MCP tool call directly"""
    print("=== MCP Tool Simulation: repo_map ===")
    print("Target: /home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder")
    print()
    
    # Simulate the exact MCP call parameters
    result = repo_map(
        project_root="/home/dundell2/Desktop/dev/reportBuilder_8-3-2025/Ecne-AI-Report-Builder",
        file_patterns=["*.py", "*.js", "*.java", "*.rb"],
        scan_directories=["."],
        verbose=True,
        token_limit=4096
    )
    
    print("✅ MCP Simulation Results:")
    print(f"Map generated: {len(result.get('map', ''))} characters")
    print(f"Files processed: {result.get('report', {}).get('total_files_considered', 0)}")
    print(f"Definitions found: {result.get('report', {}).get('definition_matches', 0)}")
    print(f"References found: {result.get('report', {}).get('reference_matches', 0)}")
    
    # Show a preview of the map
    if 'map' in result and result['map']:
        print("\n📋 Map Preview:")
        lines = result['map'].split('\n')
        for i, line in enumerate(lines[:10]):  # Show first 10 lines
            print(f"  {line}")
        if len(lines) > 10:
            print(f"  ... and {len(lines) - 10} more lines")
    
    return result

if __name__ == "__main__":
    test_mcp_simulation()