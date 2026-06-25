import joblib

model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

while True:
    text = input("Enter job description: ")

    X = vectorizer.transform([text])

    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0]

    print("\nPrediction:", "Fake" if prediction == 1 else "Genuine")
    print("Confidence:", round(max(probability) * 100, 2), "%")