"""
Test AMD API Connection
Run this to verify your backend can connect to AMD
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_amd_connection():
    """Test if AMD API credentials are configured and working"""
    
    print("=" * 60)
    print("🔍 Testing AMD API Connection")
    print("=" * 60)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("   Solution: Create .env file with your AMD credentials")
        return False
    
    # Check if credentials are set
    api_key = os.getenv("AMD_API_KEY")
    api_base = os.getenv("AMD_API_BASE_URL")
    
    if not api_key or api_key == "your_amd_api_key_here":
        print("❌ AMD_API_KEY not configured")
        print("   Solution: Add your AMD API key to .env file")
        return False
    
    if not api_base:
        print("❌ AMD_API_BASE_URL not configured")
        print("   Solution: Add AMD API base URL to .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    print(f"✅ API Base URL: {api_base}")
    
    # Try to import and initialize LLM
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model="meta/llama-3-70b-instruct",
            base_url=api_base,
            api_key=api_key,
            temperature=0.2,
            max_tokens=512,
        )
        
        print("\n🔄 Testing API call...")
        response = llm.invoke("Say 'Hello from AMD' in 3 words")
        
        print(f"✅ AMD API Connected Successfully!")
        print(f"   Response: {response.content}")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Solution: Run 'pip install langchain-openai'")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPossible solutions:")
        print("1. Verify AMD_API_KEY is correct")
        print("2. Check AMD_API_BASE_URL is correct")
        print("3. Ensure your AMD account has API access")
        print("4. Check your internet connection")
        return False

if __name__ == "__main__":
    success = test_amd_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Backend is ready to connect to AMD!")
        print("\nNext step: Test full agent pipeline")
        print("Run: python agents.py")
    else:
        print("❌ Backend connection failed")
        print("\nUse Option B (OpenAI) for quick testing")
    print("=" * 60)
