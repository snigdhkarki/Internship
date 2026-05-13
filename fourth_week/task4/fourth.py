import pandas as pd
import io


# If using your actual file, comment the 2 lines above and uncomment the line below:
df = pd.read_csv('clean_students.csv')


# ==========================================
# TASK 04: Transform & Enrich
# ==========================================

# Step 2: Add 'grade' column using apply() with a function
def assign_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 75:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'

df['grade'] = df['score'].apply(assign_grade)

# Step 3: Add 'passed' column (True if score >= 50)
df['passed'] = df['score'] >= 50

# Step 4: Add 'score_category' column ('High', 'Medium', 'Low')
def assign_category(score):
    if score >= 80:
        return 'High'
    elif score >= 50:
        return 'Medium'
    else:
        return 'Low'

df['score_category'] = df['score'].apply(assign_category)

# Step 5: Add 'rank' column (highest score gets rank 1)
# Using method='min' handles ties gracefully (e.g., two people with the top score both get rank 1)
df['rank'] = df['score'].rank(ascending=False, method='min')

# Step 6: Group by grade - print count, mean, min, and max score
print("--- Groupby Summary (By Grade) ---")
groupby_summary = df.groupby('grade')['score'].agg(['count', 'mean', 'min', 'max'])
print(groupby_summary)
print("\n" + "="*40 + "\n")

# Step 7: Sort the DataFrame by rank and reset the index
df = df.sort_values('rank').reset_index(drop=True)

# Step 8: Save enriched data and print top 5 ranked students
df.to_csv('enriched_students.csv', index=False)

print("--- Top 5 Ranked Students ---")
print(df.head(5))
print("\n" + "="*40 + "\n")

# ==========================================
# BONUS TASK
# ==========================================
# Use pivot_table() to create a summary table: grade vs subject vs average score
print("--- Bonus: Pivot Table Summary ---")
try:
    pivot_summary = pd.pivot_table(
        df, 
        values='score', 
        index='grade', 
        columns='subject', 
        aggfunc='mean'
    )
    print(pivot_summary)
except KeyError:
    print("Could not generate pivot table: 'subject' column missing from data.")