import pandas as pd

df = pd.read_csv("fake_job_postings.csv")

# Merge useful text columns
df["job_description"] = (
    df["title"].fillna("") + " " +
    df["company_profile"].fillna("") + " " +
    df["description"].fillna("") + " " +
    df["requirements"].fillna("") + " " +
    df["benefits"].fillna("")
)

# Keep only needed columns
new_df = df[["job_description", "fraudulent"]]

# Rename
new_df.columns = ["job_description", "label"]

# Save
new_df.to_csv("dataset.csv", index=False)

print("Dataset prepared successfully!")
print("Rows:", len(new_df))