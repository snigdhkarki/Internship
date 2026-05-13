import pandas as pd
import numpy as np

# --- Step 2: Load data and show initial problems ---
df = pd.read_csv('messy_students.csv')
original_row_count = len(df)

print("=== STEP 2: INITIAL DATA PROBLEMS ===")
print("Data Info:")
df.info()
print("\nMissing Values:")
print(df.isnull().sum())
print("-" * 40)

# --- Bonus Preparation: Track stats before cleaning ---
initial_nulls = df.isnull().sum().sum()
initial_dupes = df.duplicated().sum()

# --- Step 3: Fix all 6 problems ---

# 1 & 2. Fix Whitespace and Inconsistent Casing in 'name'
# Convert to string (to handle nulls safely during text ops), strip spaces, apply Title Case
df['name'] = df['name'].astype(str).str.strip().str.title()
# Turn 'Nan' strings back to actual NaNs so we can drop them easily
df['name'] = df['name'].replace('Nan', np.nan)

# 3. Fix Score stored as string (e.g., '92', ' 78 ')
# Remove any single quotes and whitespace, then convert to numeric
df['score'] = df['score'].astype(str).str.replace("'", "", regex=False).str.strip()
df['score'] = pd.to_numeric(df['score'], errors='coerce') # Invalid parsing becomes NaN

# 4. Fix Nulls (Missing score or name)
df = df.dropna(subset=['name', 'score'])

# 5. Fix Duplicate rows
df = df.drop_duplicates()

# 6. Fix Invalid values (Scores below 0)
# We can track how many are invalid before filtering them out
invalid_scores_count = len(df[df['score'] < 0])
df = df[df['score'] >= 0]

# --- Step 4: Add a grade column using apply() ---
def assign_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 75:
        return 'B'
    elif score >= 50:
        return 'C'
    else:
        return 'F'

df['grade'] = df['score'].apply(assign_grade)

# --- Step 5: Save cleaned result and print counts ---
final_row_count = len(df)
df.to_csv('clean_students.csv', index=False)

print("\n=== STEP 5: ROW COUNTS ===")
print(f"Rows before cleaning: {original_row_count}")
print(f"Rows after cleaning:  {final_row_count}")
print("-" * 40)

# --- Bonus: Full Cleaning Report ---
print("\n=== BONUS: CLEANING REPORT ===")
print(f"• Null values handled: {initial_nulls} (Rows with missing names/scores were dropped)")
print(f"• Duplicate rows removed: {initial_dupes}")
print(f"• Invalid negative scores removed: {invalid_scores_count}")
print("• All names were stripped of extra whitespace and formatted to Title Case.")
print("• All string-formatted scores were successfully cast to numeric floats.")
print("• Final output successfully saved to 'clean_students.csv'.")