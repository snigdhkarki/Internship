import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# ==========================================
# STEP 1 & 2: Create Realistic Synthetic Dataset
# ==========================================
print("Steps 1 & 2: Generating synthetic student dataset...")

num_students = 50

# Generate independent features
names = [f"Student_{i+1}" for i in range(num_students)]
study_hours = np.random.uniform(5, 25, num_students)  # 5 to 25 hours a week
sleep_hours = np.random.normal(7, 1.2, num_students)   # Mean 7 hours, std dev 1.2
attendance_pct = np.random.uniform(65, 100, num_students) # 65% to 100% attendance

# Generate score with a strong tie to study hours + attendance, plus random noise
# Base score of 20 + 2.2 points per study hour + 0.3 points per attendance percentage
noise = np.random.normal(0, 5, num_students)
score = 15 + (2.2 * study_hours) + (0.3 * attendance_pct) + noise
score = np.clip(score, 0, 100)  # Ensure scores stay within real-world 0-100 bounds

# Define passing grade as 60 or above
passed = (score >= 60).astype(int)

# Combine into a DataFrame and save to CSV
df = pd.DataFrame({
    'name': names,
    'study_hours': np.round(study_hours, 1),
    'sleep_hours': np.round(sleep_hours, 1),
    'attendance_pct': np.round(attendance_pct, 1),
    'score': np.round(score, 1),
    'passed': passed
})

df.to_csv('students.csv', index=False)
print("-> Saved dataset as 'students.csv'\n")

# ==========================================
# STEP 3: Load Data & Run EDA Checklist
# ==========================================
print("Step 3: Running full EDA Checklist...")
df_loaded = pd.read_csv('students.csv')

print(f"\n[Dataset Shape]: {df_loaded.shape}")
print("\n[Null Values Count]:")
print(df_loaded.isnull().sum())
print("\n[Descriptive Statistics]:")
print(df_loaded.describe().round(2))
print("\n[Value Counts for 'passed']:")
print(df_loaded['passed'].value_counts())
print("-" * 50)

# ==========================================
# STEP 4: Calculate Correlation Matrix
# ==========================================
print("Step 4: Calculating Correlation Matrix...")
# Drop non-numeric name column for correlation math
numeric_df = df_loaded.drop(columns=['name'])
corr_matrix = numeric_df.corr()
print("\n", corr_matrix.round(3))
print("-" * 50)

# Set global plotting style
sns.set_theme(style="white")

# ==========================================
# STEP 5: Create Annotated Seaborn Heatmap
# ==========================================
print("Step 5: Generating correlation heatmap...")
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, vmin=-1, vmax=1)
plt.title('Student Performance Metrics: Correlation Heatmap', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('heatmap.png', dpi=300)
plt.close()

# ==========================================
# STEP 6: Identify Strongest & Weakest Correlations
# ==========================================
print("Step 6: Ranking Correlations...")
# Unstack the matrix, remove self-correlations (1.0), and drop duplicates
corr_pairs = corr_matrix.unstack()
corr_pairs = corr_pairs[corr_pairs != 1.0].drop_duplicates()
# Sort pairs by absolute strength to find true relationships
sorted_pairs = corr_pairs.reindex(corr_pairs.abs().sort_values(ascending=False).index)

print("\n--- Top 3 Strongest Correlations ---")
for (var1, var2), val in sorted_pairs.head(3).items():
    print(f"{var1} & {var2}: r = {val:.3f}")

print("\n--- Top 3 Weakest Correlations ---")
for (var1, var2), val in sorted_pairs.tail(3).items():
    print(f"{var1} & {var2}: r = {val:.3f}")
print("-" * 50)

# ==========================================
# STEP 7: Plot Regression Lines for Top 2 Pairs
# ==========================================
print("Step 7: Generating Regression Scatter Plots...")
# Dynamically extract top 2 keys from our sorted pairs
top_2_pairs = list(sorted_pairs.head(2).index)

for idx, (var1, var2) in enumerate(top_2_pairs, 1):
    plt.figure(figsize=(7, 5))
    sns.regplot(x=var1, y=var2, data=df_loaded, 
                scatter_kws={'alpha':0.7, 'color':'#2c3e50'}, 
                line_kws={'color':'#e74c3c', 'linewidth':2})
    plt.title(f'Relationship Between {var1} and {var2}', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'scatter_pair_{idx}.png', dpi=300)
    plt.close()

# ==========================================
# BONUS: Pairplot Grouped by 'passed'
# ==========================================
print("Bonus Step: Generating Pairplot Cluster Chart...")
# Ensure 'passed' is treated as a categorical variable for clean legend plotting
pairplot_df = df_loaded.copy()
pairplot_df['passed'] = pairplot_df['passed'].map({1: 'Passed', 0: 'Failed'})

pp = sns.pairplot(pairplot_df.drop(columns=['name']), hue='passed', palette={'Passed': '#2ecc71', 'Failed': '#e74c3c'}, diag_kind='kde')
pp.fig.suptitle('Multi-Variable Relationships & Pass/Fail Clustering', y=1.02, fontsize=14, fontweight='bold')
plt.savefig('pairplot_clusters.png', dpi=300)
plt.close()

print("\nExecution complete! All charts saved successfully as local .png files.")

# ==========================================
# STEP 8: Written Analytical Observations (In-Code Comments)
# ==========================================
"""
--- STEP 8 ANSWERS & ANALYSIS ---

1. Does more study ALWAYS mean a higher score?
No, it does not mean an absolute guarantee for every single individual case. While the strong positive 
correlation proves that a higher study volume generally drives up scores, the injection of random 
statistical noise mimics real life. For example, a student might study 20 hours but have a rough exam day 
or poor attendance, causing them to score lower than someone who studied 16 hours but had perfect attendance. 
Correlation tracks the global trend, not an unbreakable individual rule.

2. What does the data actually say?
- Study Hours and Exam Scores have a massive, dominant positive relationship. It is the single highest 
  predictor of success in this dataset.
- Attendance also shows a mild-to-moderate positive relationship with both scores and passing rates, 
  proving that showing up provides a baseline bump to a student's final grade.
- Sleep hours show a weak, near-zero linear relationship with scores here. This indicates that while 
  sleep is crucial for health, it doesn't have a simple, straight-line relationship with grades 
  when compared to direct efforts like studying.

3. Bonus Cluster Analysis: Do passed/failed students form clear clusters?
Yes, they form highly distinct clusters, particularly noticeable in any subplot pitting 'score' or 
'study_hours' against other metrics. In the pairplot, the red 'Failed' points group tightly in the lower 
left corners (low study hours, low attendance, low scores), while the green 'Passed' points stretch upward 
and outward toward the right. The kernel density plots along the diagonal show almost completely separated 
mountains for exam scores, proving that a threshold split like a passing grade naturally separates these 
students into two distinct performance profiles.
"""