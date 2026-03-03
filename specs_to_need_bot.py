import re
import pandas as pd


# ---------- 1. Sample inventory (simulated marketplace listings) ----------
inventory_data = [
    # id, brand, model, cpu, ram_gb, storage_gb, storage_type, gpu_type, price
    [1, "Dell", "Latitude 7420", "i5", 8, 256, "SSD", "integrated", 900],
    [2, "Dell", "Latitude 7420", "i7", 16, 512, "SSD", "integrated", 1150],
    [3, "Lenovo", "ThinkPad T14", "i5", 16, 512, "SSD", "integrated", 1050],
    [4, "Lenovo", "ThinkPad T14", "i7", 16, 512, "SSD", "integrated", 1250],
    [5, "HP", "EliteBook 840", "i5", 8, 256, "SSD", "integrated", 800],
    [6, "Apple", "MacBook Pro 13", "M1", 8, 256, "SSD", "integrated", 1400],
    [7, "Apple", "MacBook Pro 13", "M1", 16, 512, "SSD", "integrated", 1800],
    [8, "Lenovo", "ThinkPad X1 Carbon", "i7", 16, 512, "SSD", "integrated", 1350],
    [9, "Dell", "G15", "i7", 16, 1000, "SSD", "dedicated", 1500],
]

inventory_cols = [
    "id",
    "brand",
    "model",
    "cpu",
    "ram_gb",
    "storage_gb",
    "storage_type",
    "gpu_type",
    "price",
]
inventory = pd.DataFrame(inventory_data, columns=inventory_cols)


# ---------- 2. NLP parsing ----------
def parse_requirements(text: str) -> dict:
    """Parse free-text user requirements into structured fields."""
    text_lower = text.lower()

    # Budget: look for a number, optionally with $ or "sgd"
    budget_match = re.search(r"\$?\s*(\d+)", text_lower)
    budget = int(budget_match.group(1)) if budget_match else None

    # Quantity (not used in filtering, but useful to show in UI)
    qty_match = re.search(r"(\d+)\s*(laptop|pc|computer|computers|laptops)", text_lower)
    quantity = int(qty_match.group(1)) if qty_match else 1

    # OS preference
    if "mac" in text_lower or "macos" in text_lower:
        os_pref = "mac"
    elif "windows" in text_lower:
        os_pref = "windows"
    else:
        os_pref = "any"

    # Job function
    if "video" in text_lower or "editing" in text_lower:
        job = "video_editing"
    elif "account" in text_lower:
        job = "accounting"
    elif "data" in text_lower or "ml" in text_lower or "ai" in text_lower:
        job = "data_science"
    elif "developer" in text_lower or "coding" in text_lower or "programming" in text_lower:
        job = "software_dev"
    else:
        job = "general_office"

    return {
        "job_function": job,
        "budget": budget,
        "quantity": quantity,
        "os_pref": os_pref,
        "raw_text": text,
    }


# ---------- 3. Map job function to minimum specs ----------
def job_to_min_specs(job: str) -> dict:
    if job == "video_editing":
        return {"min_ram": 16, "min_storage": 512, "needs_gpu": True}
    if job == "data_science":
        return {"min_ram": 16, "min_storage": 512, "needs_gpu": False}
    if job == "software_dev":
        return {"min_ram": 16, "min_storage": 512, "needs_gpu": False}
    if job == "accounting":
        return {"min_ram": 8, "min_storage": 256, "needs_gpu": False}
    return {"min_ram": 8, "min_storage": 256, "needs_gpu": False}


# ---------- 4. Recommend devices ----------
def recommend_devices(user_text: str, top_k: int = 3):
    """Return parsed requirements and top matching devices from inventory."""
    req = parse_requirements(user_text)
    spec = job_to_min_specs(req["job_function"])

    candidates = inventory[
        (inventory["ram_gb"] >= spec["min_ram"])
        & (inventory["storage_gb"] >= spec["min_storage"])
    ]

    if spec["needs_gpu"]:
        candidates = candidates[candidates["gpu_type"] == "dedicated"]

    # Budget filter (per device)
    if req["budget"]:
        candidates = candidates[candidates["price"] <= req["budget"]]

    # OS preference
    if req["os_pref"] == "mac":
        candidates = candidates[candidates["brand"] == "Apple"]
    elif req["os_pref"] == "windows":
        candidates = candidates[candidates["brand"] != "Apple"]

    candidates = candidates.sort_values("price").head(top_k)
    return req, candidates


def format_reply(req: dict, candidates: pd.DataFrame) -> str:
    """Format a human-readable reply for console or UI."""
    job_map = {
        "video_editing": "Video Editing",
        "data_science": "Data Science / Analytics",
        "software_dev": "Software Development",
        "accounting": "Accounting / Finance",
        "general_office": "General Office Work",
    }
    job_label = job_map.get(req["job_function"], "General Use")

    base_spec = job_to_min_specs(req["job_function"])

    lines = []
    lines.append(f"Interpreted need: {job_label}")
    if req["budget"]:
        lines.append(f"Budget per device: about ${req['budget']}")
    lines.append(
        "Recommended minimum specs: "
        f"{base_spec['min_ram']}GB RAM, "
        f"{base_spec['min_storage']}GB SSD, "
        f"{'dedicated GPU' if base_spec['needs_gpu'] else 'integrated GPU OK'}"
    )
    lines.append("")

    if candidates.empty:
        lines.append(
            "No matching devices found in the current inventory for this budget/spec."
        )
        return "\n".join(lines)

    lines.append("Top matching devices:")
    for _, row in candidates.iterrows():
        lines.append(
            f"- ID {row['id']}: {row['brand']} {row['model']} "
            f"({row['cpu']}, {row['ram_gb']}GB RAM, {row['storage_gb']}GB {row['storage_type']}, "
            f"GPU: {row['gpu_type']}), Price: ${row['price']}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print("Specs-to-Need Assistant (type 'exit' to quit)\n")
    while True:
        user_text = input(
            "Describe what you need (e.g. 'I need a laptop for video editing under $1500'): "
        )
        if user_text.strip().lower() in {"exit", "quit"}:
            break
        req, recs = recommend_devices(user_text)
        print()
        print(format_reply(req, recs))
        print("-" * 60)

