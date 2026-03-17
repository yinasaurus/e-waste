import re

import pandas as pd
from colorama import Fore, Style, init as colorama_init
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Simple constant FX rate used for this prototype
EUR_TO_SGD = 1.45


# Initialize colorama for Windows terminals
colorama_init(autoreset=True)


def _parse_ram_gb(ram_str: str) -> int:
    """Convert strings like '8GB' to integer 8."""
    if not isinstance(ram_str, str):
        return 0
    match = re.search(r"(\d+)", ram_str)
    return int(match.group(1)) if match else 0


def _parse_storage(memory_str: str) -> tuple[int, str]:
    """
    Convert '256GB SSD', '128GB SSD + 1TB HDD', '32GB Flash Storage' into
    (storage_gb, storage_type) focusing on the primary SSD/flash size.
    """
    if not isinstance(memory_str, str):
        return 0, "unknown"

    # Prefer SSD / Flash if present, otherwise fall back to the first capacity.
    parts = memory_str.split("+")
    primary_part = parts[0].strip()

    # Capacity in GB or TB
    gb_match = re.search(r"(\d+)\s*GB", primary_part, flags=re.IGNORECASE)
    tb_match = re.search(r"(\d+)\s*TB", primary_part, flags=re.IGNORECASE)

    storage_gb = 0
    if gb_match:
        storage_gb = int(gb_match.group(1))
    elif tb_match:
        storage_gb = int(tb_match.group(1)) * 1024

    storage_type = "HDD"
    lowered = primary_part.lower()
    if "ssd" in lowered or "flash" in lowered:
        storage_type = "SSD"

    return storage_gb, storage_type


def _derive_gpu_type(gpu_str: str) -> str:
    """Map full GPU name to 'integrated' vs 'dedicated'."""
    if not isinstance(gpu_str, str):
        return "integrated"
    lowered = gpu_str.lower()
    if "nvidia" in lowered or "radeon" in lowered:
        return "dedicated"
    return "integrated"


# ---------- 1. Load dataset from CSV ----------
# The source file is not UTF‑8 encoded, so we specify a
# more permissive encoding to avoid UnicodeDecodeError.
raw_df = pd.read_csv("laptop_price.csv", encoding="latin1")

# Engineer features to match the FMV model needs
df = pd.DataFrame()
df["brand"] = raw_df["Company"]
df["model"] = raw_df["Product"]
df["cpu"] = raw_df["Cpu"]
df["ram_gb"] = raw_df["Ram"].apply(_parse_ram_gb)
df[["storage_gb", "storage_type"]] = raw_df["Memory"].apply(
    lambda s: pd.Series(_parse_storage(s))
)
df["gpu_type"] = raw_df["Gpu"].apply(_derive_gpu_type)
df["price_eur"] = raw_df["Price_euros"]
df["price_sgd"] = df["price_eur"] * EUR_TO_SGD

# Simple cleanup: drop clearly invalid rows
df = df[df["ram_gb"] > 0]
df = df[df["storage_gb"] > 0]


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
    ]
]
y = df["price_sgd"]

categorical = ["brand", "model", "cpu", "storage_type", "gpu_type"]
numeric = ["ram_gb", "storage_gb"]

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
        "model": "XPS 13",
        "cpu": "Intel Core i5 8250U 1.6GHz",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu_type": "integrated",
    }

    fmv_price = predict_fmv(sample_device)
    print(f"\n{Fore.CYAN}Sample device:{Style.RESET_ALL} {sample_device}")
    print(
        f"{Fore.GREEN}Predicted Fair Market Value (SGD, approx):{Style.RESET_ALL} "
        f"S${fmv_price:.2f}"
    )

