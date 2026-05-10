"""
Test Script for Green Supply Chain Auditor
Run this to verify all components work before launching the full app

Usage:
    python test_system.py
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    try:
        import crewai
        import langchain_openai
        import chromadb
        import streamlit
        import pandas
        from dotenv import load_dotenv
        import sentence_transformers
        print("✅ All packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_env_file():
    """Test if .env file exists and has required keys"""
    print("\n🔍 Testing .env file...")
    if not Path(".env").exists():
        print("❌ .env file not found")
        print("Run: cp .env.example .env")
        print("Then edit .env with your AMD API credentials")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("AMD_API_KEY")
    api_base = os.getenv("AMD_API_BASE_URL")
    
    if not api_key or api_key == "your_amd_api_key_here":
        print("⚠️  .env file exists but AMD_API_KEY needs to be set")
        print("Add your AMD Developer Cloud API key to .env")
        return False
    
    print(f"✅ .env configured (API Base: {api_base})")
    return True

def test_database():
    """Test ChromaDB setup and seeding"""
    print("\n🔍 Testing ChromaDB...")
    try:
        from supplier_db import seed_database, query_suppliers
        
        # Seed database
        seed_database()
        
        # Test query
        results = query_suppliers("air freight alternative", n_results=2)
        
        if len(results) > 0:
            print(f"✅ ChromaDB working ({len(results)} suppliers found)")
            print(f"   Sample: {results[0]['supplier_name']}")
            return True
        else:
            print("❌ ChromaDB query returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_agents_basic():
    """Test agent tools without running full pipeline"""
    print("\n🔍 Testing agent tools...")
    try:
        from agents import calculate_emissions, lookup_green_suppliers, estimate_distance_km
        
        # Test distance estimation
        dist = estimate_distance_km("Shanghai -> Karachi")
        print(f"   Distance tool: Shanghai → Karachi = {dist} km")
        
        # Test emissions calculation
        test_shipment = '[{"origin":"Shanghai","destination":"Karachi","weight_tons":5,"transport_mode":"air","distance_km":4800}]'
        emissions = calculate_emissions(test_shipment)
        print(f"   Emissions tool: Working ✓")
        
        # Test supplier lookup
        suppliers = lookup_green_suppliers("air freight alternative")
        print(f"   Supplier lookup: Working ✓")
        
        print("✅ All agent tools functional")
        return True
        
    except Exception as e:
        print(f"❌ Agent tools error: {e}")
        return False

def test_llm_connection():
    """Test LLM connection (requires valid API key)"""
    print("\n🔍 Testing LLM connection...")
    try:
        from agents import llm
        
        # Simple test prompt
        response = llm.invoke("Say 'Hello from AMD'")
        
        if response and len(str(response.content)) > 0:
            print(f"✅ LLM connected: {response.content[:50]}...")
            return True
        else:
            print("⚠️  LLM responded but with empty content")
            return False
            
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        print("\nPossible solutions:")
        print("1. Verify AMD_API_KEY is correct in .env")
        print("2. Check AMD_API_BASE_URL is correct")
        print("3. Temporarily use OpenAI for testing (see README)")
        return False

def test_sample_data():
    """Test if sample CSV exists"""
    print("\n🔍 Testing sample data...")
    if Path("sample_shipments.csv").exists():
        print("✅ sample_shipments.csv found")
        import pandas as pd
        df = pd.read_csv("sample_shipments.csv")
        print(f"   {len(df)} shipments loaded")
        return True
    else:
        print("⚠️  sample_shipments.csv not found (optional)")
        return True

def main():
    print("=" * 60)
    print("🌿 Green Supply Chain Auditor - System Test")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Environment": test_env_file(),
        "Database": test_database(),
        "Agent Tools": test_agents_basic(),
        "Sample Data": test_sample_data(),
        "LLM Connection": test_llm_connection(),
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    all_critical_passed = results["Imports"] and results["Database"] and results["Agent Tools"]
    
    print("\n" + "=" * 60)
    if all_critical_passed:
        print("✅ Core system ready!")
        if not results["LLM Connection"]:
            print("⚠️  LLM connection failed - configure AMD API key to run full pipeline")
        print("\nNext steps:")
        print("1. Configure AMD API key in .env (if not done)")
        print("2. Run: streamlit run app.py")
    else:
        print("❌ Critical tests failed - fix errors before proceeding")
    print("=" * 60)

if __name__ == "__main__":
    main()
