from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Training data (basic but powerful for demo)
texts = [
    "sugar palm oil maida preservative",
    "whole grain oats nuts fiber protein",
    "high sugar refined flour unhealthy",
    "low sugar high protein healthy",
    "artificial color preservative bad",
    "natural ingredients healthy food"
]

labels = [
    0,  # unhealthy
    1,  # healthy
    0,
    1,
    0,
    1
]

# Train model
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)


def predict_health(text):
    text = text.lower()
    X_test = vectorizer.transform([text])
    prediction = model.predict(X_test)[0]

    if prediction == 1:
        return "Healthy"
    else:
        return "Unhealthy"
    