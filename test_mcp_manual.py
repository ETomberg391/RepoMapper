#!/usr/bin/env python3
"""
Manual MCP protocol test to verify server responds correctly
"""

import json
import subprocess
import sys
import time

def test_mcp_protocol():
    """Test MCP protocol communication manually"""
    print("Testing MCP protocol manually...")
    
    # Start server with stdin/stdout capture
    server = subprocess.Popen(
        [sys.executable, "repomap_server.py", "--debug"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Give server time to start
    time.sleep(2)
    
    if server.poll() is not None:
        print("Server failed to start")
        stderr = server.stderr.read()
        print("STDERR:", stderr)
        return False
    
    print("✓ Server started successfully")
    
    try:
        # Send initialization request (MCP protocol)
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "TestClient",
                    "version": "1.0.0"
                }
            }
        }
        
        server.stdin.write(json.dumps(init_request) + '\n')
        server.stdin.flush()
        
        # Read response with timeout
        try:
            response_line = server.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                print("✓ Server responded to initialization")
                print(f"   Response: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            else:
                print("✗ No response from server")
                return False
                
        except json.JSONDecodeError:
            print("✗ Invalid JSON response from server")
            return False
        except Exception as e:
            print(f"✗ Error reading response: {e}")
            return False
            
    finally:
        # Clean up
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
    
    print("✓ MCP protocol test completed successfully")
    return True

if __name__ == "__main__":
    success = test_mcp_protocol()
    sys.exit(0 if success else 1)