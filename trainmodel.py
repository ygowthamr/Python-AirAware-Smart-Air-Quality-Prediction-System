# train_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
import os

# -------------------------------
# LOAD DATASET
# -------------------------------
df = pd.read_csv("dataset1.csv")

# Clean column names
df.columns = [c.strip().replace(" ","_") for c in df.columns]

# -------------------------------
# DEFINE FEATURES & TARGET
# -------------------------------
# Adjust these to match your dataset
pollutants = ["PM2.5","PM10","NO2","SO2","CO","O3"]

# Create AQI column if not exists (simple PM2.5 based approximation)
if "AQI" not in df.columns:
    df["AQI"] = df["PM2.5"].apply(lambda x: 50 if x<=30 else
                                           100 if x<=60 else
                                           150 if x<=90 else
                                           200 if x<=120 else 300)

X = df[pollutants]
y = df["AQI"]

# -------------------------------
# TRAIN MODEL
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

# -------------------------------
# SAVE MODEL
# -------------------------------
if not os.path.exists("model"):
    os.makedirs("model")
joblib.dump(model, "air_quality_model.pkl")
print("✅ Model saved to model/air_quality_model.pkl")
