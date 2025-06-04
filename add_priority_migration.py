"""
Migration script to add missing columns to appointments table
Run this script to add the priority and payment fields to existing appointments
"""

from app import app, db
from models import Appointment
from sqlalchemy import text

def add_missing_columns():
    """Add missing columns to appointments table"""
    with app.app_context():
        try:
            # Check existing columns
            with db.engine.connect() as connection:
                result = connection.execute(text("SHOW COLUMNS FROM appointment"))
                existing_columns = [row[0] for row in result]
                print(f"Existing columns: {existing_columns}")
                
                # List of columns to add
                columns_to_add = [
                    ("priority", "VARCHAR(10) DEFAULT 'medium'"),
                    ("payment_status", "VARCHAR(20) DEFAULT 'unpaid'"),
                    ("payment_amount", "FLOAT"),
                    ("payment_mode", "VARCHAR(20)"),
                    ("payment_received_by", "INT"),
                    ("payment_date", "DATETIME")
                ]
                
                # Add columns without foreign key constraints first
                for column_name, column_definition in columns_to_add:
                    if column_name not in existing_columns:
                        try:
                            sql = f"ALTER TABLE appointment ADD COLUMN {column_name} {column_definition}"
                            connection.execute(text(sql))
                            connection.commit()
                            print(f"✅ Added column '{column_name}' successfully")
                        except Exception as e:
                            print(f"❌ Error adding column '{column_name}': {str(e)}")
                    else:
                        print(f"⚠️  Column '{column_name}' already exists")
                
                # Add foreign key constraint for payment_received_by if the column was just added
                if 'payment_received_by' not in existing_columns:
                    try:
                        # Add foreign key constraint
                        connection.execute(text(
                            "ALTER TABLE appointment ADD CONSTRAINT fk_payment_received_by "
                            "FOREIGN KEY (payment_received_by) REFERENCES user(id)"
                        ))
                        connection.commit()
                        print("✅ Added foreign key constraint for payment_received_by")
                    except Exception as e:
                        print(f"⚠️  Could not add foreign key constraint: {str(e)}")
                        print("   This is not critical - the column will still work without the constraint")
                
                # Update existing appointments with default values
                try:
                    connection.execute(text("UPDATE appointment SET priority = 'medium' WHERE priority IS NULL"))
                    connection.execute(text("UPDATE appointment SET payment_status = 'unpaid' WHERE payment_status IS NULL"))
                    connection.commit()
                    print("✅ Updated existing appointments with default values")
                except Exception as e:
                    print(f"❌ Error updating default values: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Error in migration: {str(e)}")

if __name__ == "__main__":
    add_missing_columns() 