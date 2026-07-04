import sqlite3, os

db_path = 'clinic.db'
if not os.path.exists(db_path):
    db_path = 'instance/clinic.db'

print(f'Using DB: {db_path}')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute('PRAGMA table_info(appointment)')
cols = [row[1] for row in cur.fetchall()]

if 'patient_type' in cols:
    print('patient_type column already exists — nothing to do.')
else:
    cur.execute("ALTER TABLE appointment ADD COLUMN patient_type VARCHAR(20) DEFAULT 'existing'")
    conn.commit()
    print('Successfully added patient_type column to appointment table.')

conn.close()
