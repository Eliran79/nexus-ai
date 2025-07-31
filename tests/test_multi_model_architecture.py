#!/usr/bin/env python3
"""
Test script to demonstrate the new NEXUS AI multi-model features
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nexus_ai.models import model_factory

async def test_all_features():
    print("🚀 NEXUS AI v0.3.0 - Multi-Model Local Execution Test")
    print("=" * 60)
    
    # Test model availability
    print("\n📊 Model Availability:")
    availability = model_factory.get_available_models()
    for model_name, modes in availability.items():
        print(f"  {model_name.upper()}:")
        for mode_name, available in modes.items():
            status = "✅ Available" if available else "❌ Not Available"
            print(f"    {mode_name}: {status}")
    
    # Test Claude local
    print("\n🤖 Testing Claude Local:")
    try:
        claude_local = model_factory.get_claude_local()
        response = await claude_local.get_response("What is 7 * 8?")
        print(f"   Query: What is 7 * 8?")
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Gemini local
    print("\n🧠 Testing Gemini Local:")
    try:
        gemini_local = model_factory.get_gemini_local()
        response = await gemini_local.get_response("What is the capital of France?")
        print(f"   Query: What is the capital of France?")
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test model factory defaults
    print("\n⚙️  Testing Model Factory:")
    default_model = model_factory.get_model()
    print(f"   Default model: {default_model.name}")
    print(f"   Available: {default_model.is_available()}")
    
    print("\n✅ All tests completed!")
    print("\n💡 Usage Examples:")
    print("   nexus-ai")
    print("   🔮 claude -p How do I list files?")
    print("   🔮 gemini -p What is Python?")
    print("   🔮 model status")
    print("   🔮 model set gemini")
    print("   🔮 help")

if __name__ == "__main__":
    asyncio.run(test_all_features())