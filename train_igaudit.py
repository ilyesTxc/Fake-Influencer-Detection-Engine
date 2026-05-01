import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

train = pd.read_csv("data/train.csv")
test = pd.read_csv("data/test.csv")

X_train = train.drop("fake", axis=1)
y_train = train["fake"]
X_test = test.drop("fake", axis=1)
y_test = test["fake"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

acc = accuracy_score(y_test, model.predict(X_test))
print(f"IGAudit model accuracy: {acc*100:.1f}%")

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/igaudit_clf.pkl")
print("Saved: models/igaudit_clf.pkl")
