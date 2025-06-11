#!/usr/bin/env python3
"""
Database migration script to add missing columns to the appointment table
"""

from app import app, db
import sqlalchemy as sa

def update_appointment_table():
    """Add missing columns to the appointment table"""
    with app.app_context():
        print("=== Updating Appointment Table Schema ===")
        
        # SQL commands to add missing columns
        alterations = [
            "ALTER TABLE appointment ADD COLUMN patient_type VARCHAR(20) DEFAULT 'existing'",
            "ALTER TABLE appointment ADD COLUMN priority VARCHAR(10) DEFAULT 'medium'", 
            "ALTER TABLE appointment ADD COLUMN payment_status VARCHAR(20) DEFAULT 'unpaid'",
            "ALTER TABLE appointment ADD COLUMN payment_amount FLOAT",
            "ALTER TABLE appointment ADD COLUMN payment_mode VARCHAR(20)",
            "ALTER TABLE appointment ADD COLUMN payment_received_by INTEGER",
            "ALTER TABLE appointment ADD COLUMN payment_date DATETIME",
            "ALTER TABLE appointment ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE appointment ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        ]
        
        # Add foreign key constraint for payment_received_by
        fk_constraint = """
        ALTER TABLE appointment 
        ADD CONSTRAINT fk_appointment_payment_received_by 
        FOREIGN KEY (payment_received_by) REFERENCES user(id)
        """
        
        try:
            # Execute each alteration
            for i, sql in enumerate(alterations, 1):
                try:
                    column_name = sql.split('ADD COLUMN')[1].split()[0]
                    print(f"{i}. Adding column: {column_name}")
                    
                    # Use the newer SQLAlchemy connection method
                    with db.engine.connect() as connection:
                        connection.execute(sa.text(sql))
                        connection.commit()
                    
                    print(f"   ✅ Success")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print(f"   ⚠️  Column already exists - skipping")
                    else:
                        print(f"   ❌ Error: {e}")
            
            # Add foreign key constraint
            try:
                print("10. Adding foreign key constraint for payment_received_by")
                with db.engine.connect() as connection:
                    connection.execute(sa.text(fk_constraint))
                    connection.commit()
                print("   ✅ Success")
            except Exception as e:
                if "Duplicate" in str(e) or "already exists" in str(e):
                    print("   ⚠️  Constraint already exists - skipping")
                else:
                    print(f"   ❌ Error: {e}")
            
            print("\n=== Schema Update Complete ===")
            print("The appointment table now matches the model definition!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    update_appointment_table()