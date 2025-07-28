#!/usr/bin/env python3
"""
Script to run the waiting area migration
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import WaitingArea

def run_migration():
    """Run the waiting area migration"""
    with app.app_context():
        try:
            # Create the waiting_area table
            db.create_all()
            print("✅ Waiting area table created successfully!")
            
            # Verify the table exists
            try:
                with db.engine.connect() as connection:
                    result = connection.execute(db.text("SHOW TABLES LIKE 'waiting_area'"))
                    if result.fetchone():
                        print("✅ Waiting area table verified in database")
                    else:
                        print("❌ Waiting area table not found in database")
                        return False
            except Exception as e:
                print(f"❌ Error verifying table: {str(e)}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Error creating waiting area table: {str(e)}")
            return False

if __name__ == "__main__":
    print("🚀 Running Waiting Area Migration...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    success = run_migration()
    
    if success:
        print("-" * 50)
        print("✅ Migration completed successfully!")
        print("🎉 Waiting Area module is ready to use!")
        print("\n📋 Next steps:")
        print("1. Restart your Flask application")
        print("2. Access the waiting area from the navigation menu")
        print("3. For receptionists: /waiting-area/receptionist/waiting-area")
        print("4. For doctors: /waiting-area/doctor/waiting-area")
    else:
        print("-" * 50)
        print("❌ Migration failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1) 