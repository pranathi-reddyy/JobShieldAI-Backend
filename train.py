import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

print("⏳ Loading dataset...")
df = pd.read_csv("fake_job_postings.csv")

# Clean labels
df = df.dropna(subset=["fraudulent"])

text_columns = ["title", "company_profile", "description", "requirements", "benefits"]
for col in text_columns:
    df[col] = df[col].fillna("")

# Construct full semantic content
df["job_description"] = (
    df["title"] + " " +
    df["company_profile"] + " " +
    df["description"] + " " +
    df["requirements"] + " " +
    df["benefits"]
)

df = df[df["job_description"].str.strip() != ""]

X = df["job_description"]
y = df["fraudulent"].astype(int)

print(f"📊 Class distribution:\n{y.value_counts()}")

# Vectorizer with optimized bounds to prevent overfitting on unigrams
# TF-IDF Vectorizer optimization
vectorizer = TfidfVectorizer(
    stop_words="english",
    lowercase=True, 
    max_features=12000, # Dropping max features slightly filters out random noise tokens
    ngram_range=(1, 2),  # Shifting from (1,3) to (1,2) stops the model from over-fitting on long specific phrases
    min_df=5,            # Token must appear at least 5 times in the dataset to be considered
    max_df=0.85          # Discard terms that appear in more than 85% of postings (too common)
)

print("⚙️ Vectorizing text data...")
X_vectorized = vectorizer.fit_transform(X)

print("🧠 Fitting Logistic Regression model...")
model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    C=1.0, # Regularization strength
    random_state=42
)
model.fit(X_vectorized, y)

# Save artifacts using optimal compression
joblib.dump(model, "model.pkl", compress=3)
joblib.dump(vectorizer, "vectorizer.pkl", compress=3)

print("🎉 Model and Vectorizer trained and saved successfully!")