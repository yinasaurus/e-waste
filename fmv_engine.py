import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


# ---------- 1. Create a small synthetic dataset ----------
data = [
    # brand, model, cpu, ram_gb, storage_gb, storage_type, gpu_type, age_years, battery_health, grade, price
    ["Dell", "Latitude 7420", "i5", 8, 256, "SSD", "integrated", 1, 95, "A", 950],
    ["Dell", "Latitude 7420", "i7", 16, 512, "SSD", "integrated", 2, 90, "A", 1100],
    ["Dell", "Latitude 5400", "i5", 8, 256, "SSD", "integrated", 3, 85, "B", 650],
    ["Dell", "Latitude 5400", "i5", 16, 512, "SSD", "integrated", 4, 80, "B", 600],
    ["HP", "EliteBook 840", "i5", 8, 256, "SSD", "integrated", 3, 85, "B", 620],
    ["HP", "EliteBook 840", "i7", 16, 512, "SSD", "integrated", 2, 90, "A", 980],
    ["Lenovo", "ThinkPad T14", "i5", 16, 512, "SSD", "integrated", 2, 92, "A", 1000],
    ["Lenovo", "ThinkPad T14", "i7", 16, 512, "SSD", "integrated", 1, 97, "A", 1200],
    ["Apple", "MacBook Pro 13", "M1", 8, 256, "SSD", "integrated", 2, 92, "A", 1300],
    ["Apple", "MacBook Pro 13", "M1", 16, 512, "SSD", "integrated", 1, 98, "A", 1700],
    ["Apple", "MacBook Air 13", "M1", 8, 256, "SSD", "integrated", 3, 90, "B", 1050],
    ["Lenovo", "ThinkPad X1 Carbon", "i7", 16, 512, "SSD", "integrated", 3, 85, "B", 1150],
]

columns = [
    "brand",
    "model",
    "cpu",
    "ram_gb",
    "storage_gb",
    "storage_type",
    "gpu_type",
    "age_years",
    "battery_health",
    "grade",
    "price",
]
df = pd.DataFrame(data, columns=columns)


# ---------- 2. Train FMV model ----------
X = df[
    [
        "brand",
        "model",
        "cpu",
        "ram_gb",
        "storage_gb",
        "storage_type",
        "gpu_type",
        "age_years",
        "battery_health",
        "grade",
    ]
]
y = df["price"]

categorical = ["brand", "model", "cpu", "storage_type", "gpu_type", "grade"]
numeric = ["ram_gb", "storage_gb", "age_years", "battery_health"]

preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", "passthrough", numeric),
    ]
)

model = RandomForestRegressor(n_estimators=200, random_state=42)

pipeline = Pipeline(
    steps=[
        ("preprocess", preprocess),
        ("model", model),
    ]
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
pipeline.fit(X_train, y_train)

r2 = pipeline.score(X_test, y_test)
print(f"Test R^2 score (demo on tiny synthetic data): {r2:.2f}")


# ---------- 3. Helper to predict FMV for one device ----------
def predict_fmv(device_dict: dict) -> float:
    """Predict fair market value for a single device description."""
    df_device = pd.DataFrame([device_dict])
    pred_price = pipeline.predict(df_device)[0]
    return float(pred_price)


if __name__ == "__main__":
    # Example device from a corporate seller
    sample_device = {
        "brand": "Dell",
        "model": "Latitude 7420",
        "cpu": "i5",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu_type": "integrated",
        "age_years": 3,
        "battery_health": 85,
        "grade": "B",
    }

    fmv_price = predict_fmv(sample_device)
    print("\nSample device:", sample_device)
    print(f"Predicted Fair Market Value (USD): {fmv_price:.2f}")

