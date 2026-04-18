import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    max_tokens=None,
    reasoning_format="hidden",
    timeout=None,
    max_retries=2,
)

print("Loading model artifacts...")
artifacts = joblib.load("model.pkl")
model = artifacts['model']
vectorizer = artifacts['vectorizer']

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
            domain = u.split('//')[-1].split('/')[0]
            if has_brand and all(b not in domain for b in brands if b in u):
                is_hijack = 1
        except: pass
        is_ip = 1 if any(c.isdigit() for c in u.split('/')[2:3] if c == '.') else 0
        feats.append([u_len, dot_count, has_brand, is_hijack, is_ip])
    return np.array(feats)

def llm_chek(url):
    prompt = f"System: You are a cybersecurity expert. Task: Is the URL '{url}' a known legitimate website or a phishing scam? Respond with only 'LEGIT' or 'SCAM'."
    resp=llm.invoke(prompt)
    return resp.content

def predict_vibe1(url):
    u_lower = url.lower()
    X_tfidf = vectorizer.transform([u_lower])
    X_custom = get_custom_features([u_lower])
    X_final = hstack([X_tfidf, X_custom])
    phish_prob = model.predict_proba(X_final)[0][1]
    WHITELIST = ['google.com', 'github.com', 'microsoft.com', 'amazon.com', 'apple.com', 'stackoverflow.com', 'irctc.co.in', 'pw.live']
    try:
        domain = u_lower.split('//')[-1].split('/')[0].replace('www.', '')
    except:
        domain = u_lower
    if any(domain == brand or domain.endswith('.' + brand) for brand in WHITELIST):
        phish_prob = min(phish_prob, 0.05)
    if any(bad in u_lower for bad in ['g00gle', 'paypa1', 'amaz0n']):
        phish_prob = max(phish_prob, 0.95)
    if u_lower.endswith('.xyz') or '.xyz/' in u_lower:
        phish_prob = max(phish_prob, 0.85)
    if phish_prob >= 0.70:
        llm_res = llm_chek(u_lower) # Your SLM "Judge"
        if llm_res == "LEGIT":
            verdict = "🟢 SAFE"
            phish_prob = 0.05
        else:
            verdict = "🔴 PHISH"
    else:
        verdict = "🟢 SAFE"
        
    return verdict, phish_prob

#Testing...ignore these
tough_cases = [
    "https://google.com",                          # Real Google (MUST BE SAFE)
    "https://g00gle.com/login",                    # Typosquat
    "http://paypa1-verify-account.xyz",            # Multi-layer threat
    "https://amazon-security.update-now.ru/login", # Subdomain Hijack
    "https://github.com/trending",                 # Long URL (Should be SAFE)
    "https://microsoft-office-365.com",            # Looks real but is a common phish domain
    "http://172.217.167.78/index.html",            # IP Address of Google (Suspicious in email context)
    "https://www.google.com.validate-info.tk",      # Deep Subdomain TLD trap
    "https://goog1e.com",
    "https://amazon.com",
    "https://irctc.co.in",
    "https://www.pw.live"

]


verdicts, prob = predict_vibe1("https://www.pw.live")
print(verdicts, prob)

