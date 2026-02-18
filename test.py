"""Quick test script - verify system works"""
import sys
import time

def test_imports():
    """Test all dependencies"""
    print("🧪 Testing dependencies...")
    try:
        import fastapi
        import uvicorn
        import pydantic
        import sqlalchemy
        import PIL
        import imagehash
        import requests
        print("✅ All dependencies OK")
        return True
    except ImportError as e:
        print(f"❌ Missing: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_database():
    """Test database creation"""
    print("🧪 Testing database...")
    try:
        from database.models import engine, Base, VerificationJob
        Base.metadata.create_all(engine)
        print("✅ Database OK")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_verification():
    """Test core verification logic"""
    print("🧪 Testing verification logic...")
    try:
        from services.image_analyzer import (
            extract_dates_from_text,
            extract_locations,
            extract_events
        )
        
        text = "Flooding in Bangladesh 2017 after heavy monsoon rains"
        dates = extract_dates_from_text(text)
        locs = extract_locations(text)
        events = extract_events(text)
        
        assert '2017' in dates, "Date extraction failed"
        assert 'Bangladesh' in locs, "Location extraction failed"
        assert 'flood' in events, "Event extraction failed"
        
        print("✅ Verification logic OK")
        return True
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("  VisualVerify Lite - System Test")
    print("="*50 + "\n")
    
    tests = [
        ("Dependencies", test_imports),
        ("Database", test_database),
        ("Verification", test_verification),
    ]
    
    passed = 0
    for name, test_func in tests:
        result = test_func()
        if result:
            passed += 1
        print()
    
    print("="*50)
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All tests passed! System ready.")
        print("\nRun: python main.py")
        return 0
    else:
        print("❌ Some tests failed. Fix errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
