import re

import pandas as pd
from colorama import Fore, Style, init as colorama_init


# Simple constant FX rate used for this prototype
EUR_TO_SGD = 1.45


# Initialize colorama for Windows terminals
colorama_init(autoreset=True)


def _parse_ram_gb(ram_str: str) -> int:
    if not isinstance(ram_str, str):
        return 0
    match = re.search(r"(\d+)", ram_str)
    return int(match.group(1)) if match else 0


def _parse_storage(memory_str: str) -> tuple[int, str]:
    if not isinstance(memory_str, str):
        return 0, "unknown"

    parts = memory_str.split("+")
    primary_part = parts[0].strip()

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
    if not isinstance(gpu_str, str):
        return "integrated"
    lowered = gpu_str.lower()
    if "nvidia" in lowered or "radeon" in lowered:
        return "dedicated"
    return "integrated"


# ---------- 1. Inventory from CSV (simulated marketplace listings) ----------
# The source file is not UTF‑8 encoded, so we specify a
# more permissive encoding to avoid UnicodeDecodeError.
raw_df = pd.read_csv("laptop_price.csv", encoding="latin1")

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

inventory = pd.DataFrame()
inventory["id"] = raw_df["laptop_ID"]
inventory["brand"] = raw_df["Company"]
inventory["model"] = raw_df["Product"]
inventory["cpu"] = raw_df["Cpu"]
inventory["ram_gb"] = raw_df["Ram"].apply(_parse_ram_gb)
inventory[["storage_gb", "storage_type"]] = raw_df["Memory"].apply(
    lambda s: pd.Series(_parse_storage(s))
)
inventory["gpu_type"] = raw_df["Gpu"].apply(_derive_gpu_type)
inventory["price_eur"] = raw_df["Price_euros"]
inventory["price_sgd"] = inventory["price_eur"] * EUR_TO_SGD

# Basic cleanup to avoid obviously bad rows
inventory = inventory[inventory["ram_gb"] > 0]
inventory = inventory[inventory["storage_gb"] > 0]


# ---------- 2. NLP parsing ----------
def parse_requirements(text: str) -> dict:
    """Parse free-text user requirements into structured fields."""
    text_lower = text.lower()

    # Quantity (not used directly in filtering, but useful for totals)
    qty_match = re.search(r"(\d+)\s*(laptop|pc|computer|computers|laptops)", text_lower)
    quantity_span = None
    if qty_match:
        quantity = int(qty_match.group(1))
        quantity_span = qty_match.span(1)
    else:
        # Fallback: phrases like "for 2" or "for two" (numeric only here)
        qty_for_match = re.search(r"for\s+(\d+)\b", text_lower)
        if qty_for_match:
            quantity = int(qty_for_match.group(1))
            quantity_span = qty_for_match.span(1)
        else:
            quantity = 1

    # For budget parsing, ignore the quantity part so "3 laptops" or "for 2"
    # is not treated as the budget
    if quantity_span:
        start, end = quantity_span  # just the number part
        text_for_budget = text_lower[:start] + text_lower[end:]
    else:
        text_for_budget = text_lower

    # Budget: look for phrases like "under 1500", "budget 1200", "around 1000"
    budget_pattern = r"(under|below|budget|around|less than|\$)\s*\$?\s*(\d+)"
    budget_match = re.search(budget_pattern, text_for_budget)
    if budget_match:
        budget = int(budget_match.group(2))
    else:
        # fallback: look for a standalone number, but avoid confusing it with quantity
        loose_match = re.search(r"\$?\s*(\d+)", text_for_budget)
        if loose_match:
            candidate = int(loose_match.group(1))
            # if this number is exactly the quantity (e.g. "1 laptop") and we
            # already captured quantity, treat it as quantity only, not budget
            if quantity is not None and candidate == quantity:
                budget = None
            else:
                budget = candidate
        else:
            budget = None

    # OS preference
    if "mac" in text_lower or "macos" in text_lower:
        os_pref = "mac"
    elif "windows" in text_lower:
        os_pref = "windows"
    else:
        os_pref = "any"

    # Job function / use-case (simple keyword-based)
    if (
        "video" in text_lower
        or "editing" in text_lower
        or "premiere" in text_lower
        or "after effects" in text_lower
        or "davinci" in text_lower
    ):
        job = "video_editing"
    elif (
        "photo" in text_lower
        or "photoshop" in text_lower
        or "lightroom" in text_lower
        or "graphic design" in text_lower
        or "designer" in text_lower
        or "design work" in text_lower
        or "illustrator" in text_lower
        or "canva" in text_lower
        or "figma" in text_lower
        or "indesign" in text_lower
    ):
        job = "creative_design"
    elif (
        "account" in text_lower
        or "finance" in text_lower
        or "bookkeep" in text_lower
        or "excel" in text_lower
        or "spreadsheets" in text_lower
        or "quickbooks" in text_lower
        or "xero" in text_lower
    ):
        job = "accounting"
    elif (
        "data" in text_lower
        or "ml" in text_lower
        or "ai" in text_lower
        or "analytics" in text_lower
        or "analysis" in text_lower
        or "tableau" in text_lower
        or "power bi" in text_lower
        or "sql" in text_lower
    ):
        job = "data_science"
    elif (
        "developer" in text_lower
        or "coding" in text_lower
        or "code" in text_lower
        or "programming" in text_lower
        or "software engineer" in text_lower
        or "web dev" in text_lower
        or "python" in text_lower
        or "java " in text_lower
        or "c++" in text_lower
        or "javascript" in text_lower
        or "vscode" in text_lower
        or "visual studio" in text_lower
        or "github" in text_lower
    ):
        job = "software_dev"
    elif (
        "student" in text_lower
        or "school" in text_lower
        or "uni " in text_lower
        or "university" in text_lower
        or "college" in text_lower
        or "study" in text_lower
        or "homework" in text_lower
        or "assignments" in text_lower
        or "lecture" in text_lower
        or "notes" in text_lower
    ):
        job = "student_use"
    elif (
        "gaming" in text_lower
        or "games" in text_lower
        or "game" in text_lower
        or "valorant" in text_lower
        or "dota" in text_lower
        or "csgo" in text_lower
        or "league of legends" in text_lower
        or "steam" in text_lower
    ):
        job = "gaming"
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
    if job == "creative_design":
        return {"min_ram": 16, "min_storage": 512, "needs_gpu": True}
    if job == "data_science":
        return {"min_ram": 16, "min_storage": 512, "needs_gpu": False}
    if job == "software_dev":
        return {"min_ram": 16, "min_storage": 512, "needs_gpu": False}
    if job == "accounting":
        return {"min_ram": 8, "min_storage": 256, "needs_gpu": False}
    if job == "student_use":
        return {"min_ram": 8, "min_storage": 256, "needs_gpu": False}
    if job == "gaming":
        return {"min_ram": 16, "min_storage": 512, "needs_gpu": True}
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

    # Budget filter (per device), interpreted as SGD
    if req["budget"]:
        candidates = candidates[candidates["price_sgd"] <= req["budget"]]

    # OS preference
    if req["os_pref"] == "mac":
        candidates = candidates[candidates["brand"] == "Apple"]
    elif req["os_pref"] == "windows":
        candidates = candidates[candidates["brand"] != "Apple"]

    candidates = candidates.sort_values("price_sgd").head(top_k)
    return req, candidates


def format_reply(req: dict, candidates: pd.DataFrame) -> str:
    """Format a human-readable (and slightly colorful) reply for console or UI."""
    job_map = {
        "video_editing": "Video Editing",
        "creative_design": "Photo / Graphic Design",
        "data_science": "Data Science / Analytics",
        "software_dev": "Software Development",
        "accounting": "Accounting / Finance",
        "student_use": "Student / School Use",
        "gaming": "Gaming",
        "general_office": "General Office Work",
    }
    job_label = job_map.get(req["job_function"], "General Use")

    base_spec = job_to_min_specs(req["job_function"])

    lines = []
    lines.append(f"{Fore.CYAN}Interpreted need:{Style.RESET_ALL} {job_label}")
    lines.append(f"{Fore.CYAN}Quantity:{Style.RESET_ALL} {req['quantity']} device(s)")
    if req["budget"]:
        lines.append(
            f"{Fore.CYAN}Budget per device:{Style.RESET_ALL} about S${req['budget']}"
        )
    lines.append(
        f"{Fore.CYAN}Recommended minimum specs:{Style.RESET_ALL} "
        f"{base_spec['min_ram']}GB RAM, "
        f"{base_spec['min_storage']}GB SSD, "
        f"{'dedicated GPU' if base_spec['needs_gpu'] else 'integrated GPU OK'}"
    )
    lines.append("")

    if candidates.empty:
        lines.append(
            f"{Fore.RED}No matching devices found in the current inventory for this budget/spec.{Style.RESET_ALL}"
        )
        return "\n".join(lines)

    lines.append(
        f"{Fore.GREEN}Top matching devices (per device, prices in SGD, approx):{Style.RESET_ALL}"
    )
    for _, row in candidates.iterrows():
        price_sgd = row["price_sgd"]
        total_price = price_sgd * req["quantity"]
        lines.append(
            f"{Fore.YELLOW}- ID {row['id']}{Style.RESET_ALL}: "
            f"{Fore.MAGENTA}{row['brand']} {row['model']}{Style.RESET_ALL} "
            f"({row['cpu']}, {row['ram_gb']}GB RAM, {row['storage_gb']}GB {row['storage_type']}, "
            f"GPU: {row['gpu_type']}), "
            f"{Fore.GREEN}Price per device:{Style.RESET_ALL} S${price_sgd:.0f}, "
            f"{Fore.GREEN}Estimated total for {req['quantity']}:{Style.RESET_ALL} S${total_price:.0f}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print("Specs-to-Need Assistant (type 'exit' to quit)\n")
    try:
        while True:
            user_text = input(
                "Describe what you need (e.g. 'I need 3 laptops for video editing under 1500'): "
            )
            if user_text.strip().lower() in {"exit", "quit"}:
                break
            req, recs = recommend_devices(user_text)
            print()
            print(format_reply(req, recs))
            print("-" * 60)
    except KeyboardInterrupt:
        print("\nExiting assistant.")

