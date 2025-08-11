#!/usr/bin/env python3
"""
Test the enhanced content system
"""

from dotenv import load_dotenv
load_dotenv()

import os

def test_environment():
    """Test environment setup"""
    print("🔧 Environment Check:")
    print(f"   OPENAI_API_KEY: {'✅ SET' if os.getenv('OPENAI_API_KEY') else '❌ NOT SET'}")
    print(f"   APIFY_TOKEN: {'✅ SET' if os.getenv('APIFY_TOKEN') else '❌ NOT SET'}")
    print(f"   ASSEMBLYAI_TOKEN: {'✅ SET' if os.getenv('ASSEMBLYAI_TOKEN') else '❌ NOT SET'}")
    print()

def test_hardcoded_patterns():
    """Test hardcoded mentor patterns"""
    print("🧠 Testing Hardcoded Mentor Patterns:")
    try:
        from core.hardcoded_mentor_patterns import (
            get_mentor_inspired_hook,
            get_mentor_inspired_cta,
            ALL_MENTOR_PATTERNS
        )
        
        print("   ✅ Mentor patterns imported successfully")
        
        # Test pattern access
        alex_hooks = len(ALL_MENTOR_PATTERNS['alex_hormozi']['successful_hooks'])
        vaibhav_hooks = len(ALL_MENTOR_PATTERNS['vaibhav_sisinty']['successful_hooks'])
        
        print(f"   📱 Alex Hormozi: {alex_hooks} hooks available")
        print(f"   📱 Vaibhav Sisinty: {vaibhav_hooks} hooks available")
        
        # Test dynamic generation
        sample_hook = get_mentor_inspired_hook("business")
        sample_cta = get_mentor_inspired_cta()
        
        print(f"   🎣 Sample hook: {sample_hook[:50]}...")
        print(f"   💬 Sample CTA: {sample_cta}")
        print()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_enhanced_calendar():
    """Test enhanced calendar generation"""
    print("📅 Testing Enhanced Calendar Generation:")
    try:
        from core.enhanced_calendar_generator import generate_enhanced_calendar
        
        trends = ["AI tools for entrepreneurs", "business scaling strategies"]
        month = "February 2025"
        
        print(f"   🎯 Generating calendar for {month} with trends: {trends}")
        
        calendar_result = generate_enhanced_calendar(trends, month)
        
        if calendar_result and len(calendar_result) > 100:
            print("   ✅ Calendar generated successfully!")
            print(f"   📊 Length: {len(calendar_result):,} characters")
            
            # Check for mentor patterns in result
            if "Alex Hormozi" in calendar_result:
                print("   🧠 Contains Alex Hormozi patterns")
            if "Vaibhav Sisinty" in calendar_result:
                print("   🧠 Contains Vaibhav Sisinty patterns")
            if "Enhanced calendar generated" in calendar_result:
                print("   🚀 Enhanced generation confirmed")
                
            return True
        else:
            print("   ❌ Calendar generation failed or too short")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_rag_system():
    """Test RAG system (if available)"""
    print("🔍 Testing RAG System:")
    try:
        from core.rag_retrieval import RAGRetriever
        
        retriever = RAGRetriever()
        stats = retriever.get_stats()
        
        if stats:
            print("   ✅ RAG system accessible")
            print(f"   📊 Stats: {stats}")
            
            # Try a test query
            results = retriever.retrieve("business growth", limit=3)
            print(f"   🎯 Test query returned {len(results)} results")
            
            return True
        else:
            print("   ⚠️ RAG system accessible but no data (expected if pipeline not run)")
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing AI Content Strategist Enhanced System")
    print("=" * 60)
    
    # Test environment
    test_environment()
    
    # Test components
    tests = [
        ("Hardcoded Patterns", test_hardcoded_patterns),
        ("Enhanced Calendar", test_enhanced_calendar),
        ("RAG System", test_rag_system),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ {test_name} failed: {e}")
            results[test_name] = False
        print()
    
    # Summary
    print("📋 Test Summary:")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n🎯 Overall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All systems operational!")
    elif passed_count >= 2:
        print("⚡ Core systems working! RAG pipeline available when API keys added.")
    else:
        print("⚠️ Some systems need attention.")

if __name__ == "__main__":
    main()