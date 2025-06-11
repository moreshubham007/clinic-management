"""
Database migration to add patient_type column
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Appointment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_uri_here'  # Update this
db.init_app(app)

def migrate_patient_type():
    with app.app_context():
        try:
            # Check if column exists
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('appointment')]
            
            if 'patient_type' not in columns:
                # Add the column
                db.engine.execute('ALTER TABLE appointment ADD COLUMN patient_type VARCHAR(20) DEFAULT "existing"')
                print("✅ Successfully added patient_type column")
            else:
                print("✅ patient_type column already exists")
                
            # Update existing records to have 'existing' as default
            db.engine.execute('UPDATE appointment SET patient_type = "existing" WHERE patient_type IS NULL')
            print("✅ Updated existing appointments with default patient_type")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    migrate_patient_type() 