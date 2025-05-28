"""
Run this script to add the patient_type column to existing appointments
"""
from app import app, db

def add_patient_type_column():
    with app.app_context():
        try:
            # Add the column
            db.engine.execute("ALTER TABLE appointment ADD COLUMN patient_type VARCHAR(20) DEFAULT 'existing'")
            print("Successfully added patient_type column to appointment table")
        except Exception as e:
            print(f"Error adding column: {e}")
            # Column might already exist

if __name__ == "__main__":
    add_patient_type_column() 