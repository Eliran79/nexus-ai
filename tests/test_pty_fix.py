#!/usr/bin/env python3
"""Test script for PTY implementation fixes"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_ai.core.session import Session
from nexus_ai.core.executor import CodeExecutor

def test_interactive_commands():
    """Test that interactive commands work with PTY"""
    print("Testing PTY implementation for interactive commands\n")
    
    # Create a session and executor
    session = Session()
    executor = CodeExecutor(session)
    
    # Test 1: Check if 'yay' is recognized as interactive
    print("Test 1: Is 'yay' recognized as interactive?")
    is_interactive = executor.is_likely_interactive("yay -Ss test")
    print(f"Result: {is_interactive}")
    assert is_interactive, "'yay' should be recognized as interactive"
    print("✓ Passed\n")
    
    # Test 2: Test simple interactive command
    print("Test 2: Testing simple interactive command (echo with prompt)")
    print("Running: bash -c 'read -p \"Enter something: \" input; echo \"You entered: $input\"'")
    print("(You'll need to type something and press Enter)")
    stdout, stderr = executor.execute_bash("bash -c 'read -p \"Enter something: \" input; echo \"You entered: $input\"'")
    if stderr:
        print(f"Error: {stderr}")
    else:
        print(f"Result: {stdout}")
    print()
    
    # Test 3: Test that Ctrl+C works properly
    print("Test 3: Testing Ctrl+C handling")
    print("Running: bash -c 'while true; do echo \"Press Ctrl+C to stop...\"; sleep 1; done'")
    print("(Press Ctrl+C to stop the loop)")
    stdout, stderr = executor.execute_bash("bash -c 'while true; do echo \"Press Ctrl+C to stop...\"; sleep 1; done'")
    print(f"Result: {stdout}")
    if stderr:
        print(f"Error: {stderr}")
    print()
    
    print("All tests completed!")
    print("\nTo test with yay, run NEXUS and try:")
    print("  !yay -Ss <package>")
    print("  Then select packages with format like '2-121'")
    print("\nThe terminal should remain responsive after input.")

if __name__ == "__main__":
    test_interactive_commands()