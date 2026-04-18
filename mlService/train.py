import pandas as pd
import numpy as np
import time
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from scipy.sparse import hstack
print("Loading dataset...")
df = pd.read_csv("dataset.csv")
df = df.rename(columns={"type": "label", "url": "url"})
df["label"] = df["label"].str.lower().str.strip()
label_mapping = {"benign": 0, "phishing": 1, "malware": 1, "defacement": 1}
df["label"] = df["label"].map(label_mapping).fillna(0).astype(int)

print("Balancing classes (1:1 Ratio)...")
phish_df = df[df['label'] == 1]
benign_df = df[df['label'] == 0]
sample_size = min(len(phish_df), len(benign_df), 50000) 
df_balanced = pd.concat([
    phish_df.sample(sample_size, random_state=42),
    benign_df.sample(sample_size, random_state=42)
]).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Training on {len(df_balanced)} rows.")
def get_custom_features(urls):
    brands = ['google', 'paypal', 'amazon', 'microsoft', 'netflix', 'github', 'facebook']
    feats = []
    for url in urls:
        u = str(url).lower()
        u_len = len(u)
        dot_count = u.count('.')
        has_brand = 1 if any(b in u for b in brands) else 0
        is_hijack = 0
        try:
            domain = u.split('/')[2] if '//' in u else u.split('/')[0]
            if has_brand and all(b not in domain for b in brands if b in u):
                is_hijack = 1
        except: pass
        is_ip = 1 if any(char.isdigit() for char in u.split('/')[2:3] if char == '.') else 0
        
        feats.append([u_len, dot_count, has_brand, is_hijack, is_ip])
    return np.array(feats)


X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    df_balanced["url"], df_balanced["label"], test_size=0.2, random_state=42
)

print("Vectorizing (Character N-grams)...")
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4), max_features=10000)

t1 = time.time()
X_train_tfidf = vectorizer.fit_transform(X_train_raw)
X_test_tfidf = vectorizer.transform(X_test_raw)
X_train_custom = get_custom_features(X_train_raw)
X_test_custom = get_custom_features(X_test_raw)
X_train_final = hstack([X_train_tfidf, X_train_custom])
X_test_final = hstack([X_test_tfidf, X_test_custom])
print(f"Features ready in {time.time() - t1:.2f}s")
print("Training Random Forest...")
model = RandomForestClassifier(n_estimators=100, max_depth=15, n_jobs=-1)
model.fit(X_train_final, y_train)
print("\nEvaluation Summary:")
preds = model.predict(X_test_final)
print(classification_report(y_test, preds))

joblib.dump({
    'model': model,
    'vectorizer': vectorizer,
    'features_count': 5
}, "model.pkl")

print("model trained ji...phewww, finally done")
