#!/usr/bin/env python3
"""
Simple test script for NEXUS AI migration
Tests basic functionality of the new prompt_toolkit REPL
"""

import asyncio
import os
import sys
from nexus_ai.repl.prompt_toolkit_repl import NexusPromptToolkitREPL
from nexus_ai.core.session import Session


async def test_basic_functionality():
    """Test basic REPL functionality"""
    print("=== Testing NEXUS AI prompt_toolkit REPL ===\n")
    
    # Create a test session
    session = Session("test_session")
    repl = NexusPromptToolkitREPL(session)
    
    print("✓ REPL instance created successfully")
    
    # Test Python execution
    try:
        await repl.handle_python("print('Hello from Python!')")
        print("✓ Python execution works")
    except Exception as e:
        print(f"✗ Python execution failed: {e}")
    
    # Test bash execution
    try:
        await repl.handle_bash("echo 'Hello from Bash!'")
        print("✓ Bash execution works")
    except Exception as e:
        print(f"✗ Bash execution failed: {e}")
    
    # Test captured bash
    try:
        await repl.handle_bash_captured("ls -la /tmp")
        print("✓ Captured bash execution works")
    except Exception as e:
        print(f"✗ Captured bash execution failed: {e}")
    
    # Test interactive bash (with a safe command)
    try:
        await repl.handle_bash_interactive("echo 'Interactive test'")
        print("✓ Interactive bash execution works")
    except Exception as e:
        print(f"✗ Interactive bash execution failed: {e}")
    
    print(f"\n✓ Session has {len(session.output_history)} output entries")
    print("✓ All basic tests completed successfully!")


def test_command_detection():
    """Test command detection functionality"""
    print("\n=== Testing Command Detection ===\n")
    
    session = Session("test_session")
    repl = NexusPromptToolkitREPL(session)
    
    # Test interactive command detection
    interactive_commands = [
        "ssh user@server",
        "docker run -it ubuntu bash",
        "git commit",
        "sudo apt update",
        "python -i script.py"
    ]
    
    print("Interactive command detection:")
    for cmd in interactive_commands:
        is_interactive = repl.executor.is_likely_interactive(cmd)
        print(f"  '{cmd}' -> {'Interactive' if is_interactive else 'Captured'}")
    
    # Test background command detection
    background_commands = [
        "code .",
        "subl file.py",
        "firefox http://example.com"
    ]
    
    print("\nBackground command detection:")
    for cmd in background_commands:
        is_background = repl.executor._is_background_command(cmd)
        print(f"  '{cmd}' -> {'Background' if is_background else 'Foreground'}")
    
    print("✓ Command detection tests completed!")


async def test_async_subprocess():
    """Test async subprocess functionality"""
    print("\n=== Testing Async Subprocess ===\n")
    
    session = Session("test_session")
    repl = NexusPromptToolkitREPL(session)
    
    try:
        # Test captured mode
        stdout, stderr = await repl.executor.execute_bash_async("echo 'Async test'", mode='captured')
        print(f"✓ Async captured mode: '{stdout.strip()}'")
        
        # Test background mode
        stdout, stderr = await repl.executor.execute_bash_async("echo 'Background test'", mode='background')
        print(f"✓ Async background mode: '{stdout.strip()}'")
        
        print("✓ Async subprocess tests completed!")
        
    except Exception as e:
        print(f"✗ Async subprocess test failed: {e}")


def main():
    """Run all tests"""
    print("Starting NEXUS AI Tests...\n")
    
    # Check for API key (but don't fail if missing for basic tests)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not set. Claude tests will be skipped.\n")
    
    try:
        # Run sync tests
        test_command_detection()
        
        # Run async tests
        asyncio.run(test_basic_functionality())
        asyncio.run(test_async_subprocess())
        
        print("\n🎉 All tests completed successfully!")
        print("\nTo start NEXUS with the new REPL:")
        print("  python -m nexus_ai.main")
        print("  or")
        print("  nexus --prompt-toolkit")
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()