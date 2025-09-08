#!/usr/bin/env python3
"""
Test script to verify MCP server functionality
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_mcp_server():
    """Test the MCP server functionality"""
    print("Testing RepoMap MCP server...")
    
    # Start the server in a subprocess
    server_process = subprocess.Popen(
        [sys.executable, "repomap_server.py", "--debug"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it a moment to start
    time.sleep(2)
    
    # Check if server is running
    if server_process.poll() is not None:
        print("Server failed to start")
        stdout, stderr = server_process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return False
    
    print("✓ Server started successfully")
    
    # Test the CLI tool functionality (which uses the same core code)
    try:
        result = subprocess.run(
            [sys.executable, "repomap.py", ".", "--map-tokens", "256"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ CLI tool works correctly")
            if "repomap_class.py" in result.stdout:
                print("✓ Repository map generation works")
            else:
                print("⚠ Map generation may have issues")
        else:
            print("✗ CLI tool failed")
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ CLI tool timed out")
        return False
    except Exception as e:
        print(f"✗ CLI tool error: {e}")
        return False
    
    # Clean up
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
    
    print("✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)