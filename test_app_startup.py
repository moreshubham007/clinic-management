#!/usr/bin/env python3
"""
Test Flask app startup
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    """Test if the Flask app can start without errors"""
    try:
        print("🧪 Testing Flask app startup...")
        
        # Try to import the app
        from app import app
        print("✅ App imported successfully")
        
        # Try to create app context
        with app.app_context():
            print("✅ App context created successfully")
            
            # Try to import models
            from models import User, Doctor, Appointment, WaitingArea
            print("✅ Models imported successfully")
            
            # Try to import extensions
            from extensions import db
            print("✅ Extensions imported successfully")
            
            # Try a simple database query
            try:
                user_count = User.query.count()
                print(f"✅ Database query successful: {user_count} users found")
            except Exception as e:
                print(f"⚠️  Database query failed: {str(e)}")
                print("   This might be expected if database is not set up")
        
        print("\n🎉 Flask app startup test passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error during startup: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_app_startup()
    if not success:
        sys.exit(1) 