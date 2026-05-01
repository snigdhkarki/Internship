import sqlite3

def assign_grade(score):
    """Returns A/B/C/D/F based on score (Step 3)."""
    if score >= 90: return 'A'
    if score >= 80: return 'B'
    if score >= 70: return 'C'
    if score >= 60: return 'D'
    return 'F'

def run_grade_system():
    # 1. Create grades.db and students table
    conn = sqlite3.connect('grades.db')
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT,
            score INTEGER,
            grade TEXT
        )
    ''')

    # 2. Sample data for 15 students (Step 2)
    # Including a duplicate to test Step 8
    raw_data = [
        ("Alice", "Math", 95), ("Bob", "Math", 42), ("Charlie", "Math", 78),
        ("David", "Math", 88), ("Eve", "Math", 55), ("Frank", "Math", 49),
        ("Grace", "Math", 91), ("Heidi", "Math", 63), ("Ivan", "Math", 72),
        ("Judy", "Math", 45), ("Karl", "Math", 82), ("Linda", "Math", 67),
        ("Mallory", "Math", 51), ("Niaj", "Math", 99), ("Oscar", "Math", 40),
        ("Alice", "Math", 95) # Duplicate name for Step 8 check
    ]

    # 8. Handle duplicate names before inserting
    print("Processing insertions...")
    for name, subject, score in raw_data:
        cursor.execute("SELECT id FROM students WHERE name = ?", (name,))
        if cursor.fetchone():
            print(f"Skipping duplicate entry: {name}")
        else:
            cursor.execute("INSERT INTO students (name, subject, score) VALUES (?, ?, ?)", 
                           (name, subject, score))

    # 4. UPDATE all rows - set the grade column using assign_grade function
    cursor.execute("SELECT id, score FROM students")
    rows = cursor.fetchall()
    for student_id, score in rows:
        letter_grade = assign_grade(score)
        cursor.execute("UPDATE students SET grade = ? WHERE id = ?", (letter_grade, student_id))

    # 5. DELETE all students who scored below 50
    print("Removing students with scores below 50...")
    cursor.execute("DELETE FROM students WHERE score < 50")

    # 6. Add a new column 'passed' using ALTER TABLE and set based on score >= 50
    print("Updating table schema and passing status...")
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN passed BOOLEAN")
    except sqlite3.OperationalError:
        pass # Column already exists
    
    cursor.execute("UPDATE students SET passed = (score >= 50)")

    conn.commit()

    # 7. Query: show count of students per grade, ordered from A to F
    print("\n--- Student Count Per Grade ---")
    cursor.execute('''
        SELECT grade, COUNT(*) 
        FROM students 
        GROUP BY grade 
        ORDER BY grade ASC
    ''')
    for row in cursor.fetchall():
        print(f"Grade {row[0]}: {row[1]} students")

    # Final visual check of the table
    print("\n--- Final Student List ---")
    cursor.execute("SELECT name, score, grade, passed FROM students")
    for row in cursor.fetchall():
        status = "Pass" if row[3] else "Fail"
        print(f"{row[0]:<10} | Score: {row[1]} | Grade: {row[2]} | Status: {status}")

    conn.close()

if __name__ == "__main__":
    run_grade_system()