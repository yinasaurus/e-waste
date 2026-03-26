import re
from pathlib import Path

import pandas as pd
from colorama import Fore, Style, init as colorama_init


# Project data directory (CSV files live in ./data/)
DATA_DIR = Path(__file__).resolve().parent / "data"

# Simple constant FX rates used for this prototype
# (kept simple and approximate for demo purposes)
EUR_TO_SGD = 1.45   # laptop & keyboard prices are treated as EUR-like
INR_TO_SGD = 0.016  # smartphone prices come in INR-like units
USD_TO_SGD = 1.35   # iPad prices in USD


# Initialize colorama for Windows terminals
colorama_init(autoreset=True)


def estimate_used_price(
    new_price: float,
    age_years: float | None = None,
    condition: str | None = None,
    rarity: str | None = None,
) -> float:
    """
    Simple 2nd-hand pricing heuristic for this prototype.
    - Start at 2/3 of new.
    - Age reduces value a bit.
    - Bad condition reduces further, mint slightly increases.
    - Rare / discontinued items can be nudged up.
    """
    if new_price is None:
        return 0.0

    price = float(new_price) * 0.66  # base 2/3 rule

    # Age adjustment (rough, optional)
    if age_years is not None:
        if age_years > 8:
            price *= 0.6
        elif age_years > 5:
            price *= 0.7
        elif age_years > 3:
            price *= 0.8
        elif age_years > 1:
            price *= 0.9

    # Condition
    if condition:
        cond = str(condition).lower()
        if "mint" in cond or "like new" in cond or cond == "a":
            price *= 1.05
        elif cond == "b" or "fair" in cond or "used" in cond:
            price *= 0.9
        elif "poor" in cond or "parts" in cond:
            price *= 0.6

    # Rarity / desirability
    if rarity:
        rare = str(rarity).lower()
        if "rare" in rare or "sought" in rare or "discontinued" in rare:
            price *= 1.1

    return round(price, 2)


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


# ---------- 1. Laptop inventory from CSV ----------
# The source file is not UTF‑8 encoded, so we specify a
# more permissive encoding to avoid UnicodeDecodeError.
laptop_raw = pd.read_csv(DATA_DIR / "laptop_price.csv", encoding="latin1")

laptop_inventory = pd.DataFrame()
laptop_inventory["id"] = laptop_raw["laptop_ID"]
laptop_inventory["brand"] = laptop_raw["Company"]
laptop_inventory["model"] = laptop_raw["Product"]
laptop_inventory["cpu"] = laptop_raw["Cpu"]
laptop_inventory["ram_gb"] = laptop_raw["Ram"].apply(_parse_ram_gb)
laptop_inventory[["storage_gb", "storage_type"]] = laptop_raw["Memory"].apply(
    lambda s: pd.Series(_parse_storage(s))
)
laptop_inventory["gpu_type"] = laptop_raw["Gpu"].apply(_derive_gpu_type)
laptop_inventory["price_eur"] = laptop_raw["Price_euros"]
laptop_inventory["price_sgd"] = laptop_inventory["price_eur"] * EUR_TO_SGD

# Basic cleanup to avoid obviously bad laptop rows
laptop_inventory = laptop_inventory[laptop_inventory["ram_gb"] > 0]
laptop_inventory = laptop_inventory[laptop_inventory["storage_gb"] > 0]


# ---------- 1b. Mouse inventory ----------
# Mouse recommendations are currently disabled; we keep an empty DataFrame
# so the rest of the code can treat it uniformly.
mouse_inventory = pd.DataFrame()


# ---------- 1c. Keyboard inventory from CSV ----------
keyboard_raw = pd.read_csv(DATA_DIR / "all_keyboards.csv", encoding="latin1")

keyboard_inventory = pd.DataFrame()
keyboard_inventory["id"] = keyboard_raw[keyboard_raw.columns[0]]
keyboard_inventory["name"] = keyboard_raw["Name"]
keyboard_inventory["price_eur"] = pd.to_numeric(
    keyboard_raw["Price"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.replace(" ", ""),
    errors="coerce",
)
keyboard_inventory["price_sgd"] = keyboard_inventory["price_eur"] * EUR_TO_SGD
keyboard_inventory["type"] = keyboard_raw["Type"]
keyboard_inventory["connection"] = keyboard_raw["Connection"]
keyboard_inventory["rating"] = pd.to_numeric(
    keyboard_raw["Rating"], errors="coerce"
)
keyboard_inventory["votes"] = pd.to_numeric(
    keyboard_raw["Votes"], errors="coerce"
)

keyboard_inventory = keyboard_inventory.dropna(subset=["price_eur"])


# ---------- 1d. Phone inventory from CSV ----------
# Use "Mobile phone price.csv" (price in USD-like units). We convert to SGD.
# To avoid header-name quirks (BOMs, trailing spaces), we index by column order.
phones_raw = pd.read_csv(DATA_DIR / "Mobile phone price.csv", encoding="latin1")

phone_inventory = pd.DataFrame()
phone_inventory["id"] = range(1, len(phones_raw) + 1)
# Column order from sample:
# 0 Brand, 1 Model, 2 Storage , 3 RAM , 4 Screen Size (inches),
# 5 Camera (MP), 6 Battery Capacity (mAh), 7 Price ($)
phone_inventory["brand"] = phones_raw.iloc[:, 0]
phone_inventory["model"] = phones_raw.iloc[:, 1]

price_series = phones_raw.iloc[:, 7]
phone_inventory["price_usd"] = pd.to_numeric(price_series, errors="coerce")
phone_inventory["price_sgd"] = phone_inventory["price_usd"] * USD_TO_SGD

ram_series = phones_raw.iloc[:, 3].astype(str).str.replace("GB", "", regex=False)
phone_inventory["ram_gb"] = pd.to_numeric(ram_series, errors="coerce")

storage_series = phones_raw.iloc[:, 2].astype(str).str.replace("GB", "", regex=False)
phone_inventory["storage_gb"] = pd.to_numeric(storage_series, errors="coerce")

phone_inventory["battery_mah"] = pd.to_numeric(phones_raw.iloc[:, 6], errors="coerce")
phone_inventory["screen_size"] = pd.to_numeric(phones_raw.iloc[:, 4], errors="coerce")
phone_inventory["rear_cam_mp"] = phones_raw.iloc[:, 5].astype(str)

phone_inventory = phone_inventory.dropna(subset=["price_usd"])


# ---------- 1e. iPad inventory from Apple global sales CSV ----------
ipad_raw = pd.read_csv(DATA_DIR / "apple_global_sales_dataset.csv", encoding="latin1")

ipad_raw = ipad_raw[ipad_raw["category"] == "iPad"].copy()

ipad_inventory = pd.DataFrame()
ipad_inventory["id"] = range(1, len(ipad_raw) + 1)
ipad_inventory["product_name"] = ipad_raw["product_name"]
ipad_inventory["storage"] = ipad_raw["storage"]
ipad_inventory["color"] = ipad_raw["color"]
ipad_inventory["unit_price_usd"] = pd.to_numeric(
    ipad_raw["discounted_price_usd"], errors="coerce"
)
ipad_inventory["price_sgd"] = ipad_inventory["unit_price_usd"] * USD_TO_SGD
ipad_inventory["country"] = ipad_raw["country"]
ipad_inventory["year"] = ipad_raw["year"]
ipad_inventory["segment"] = ipad_raw["customer_segment"]
ipad_inventory["rating"] = pd.to_numeric(
    ipad_raw["customer_rating"], errors="coerce"
)

ipad_inventory = ipad_inventory.dropna(subset=["unit_price_usd"])


# ---------- 1f. Desktop components inventory from Newegg CSV ----------
# `newegg.csv` is a parts catalog (CPU / RAM / Storage / GPU / ...), not
# full pre-built desktop bundles. We recommend a desktop build as matched
# parts based on the user's job function + budget.

def _newegg_clean_numeric(s: object) -> float:
    """Parse numeric strings like '14,723.99' or '(691)' into floats."""
    if isinstance(s, pd.Series):
        text = (
            s.astype(str)
            .str.strip()
            .str.replace(",", "", regex=False)
            .str.replace("(", "", regex=False)
            .str.replace(")", "", regex=False)
        )
        return pd.to_numeric(text, errors="coerce")
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return float("nan")
    text = str(s).strip()
    # Remove common thousands separators and parentheses wrappers.
    text = text.replace(",", "").replace("(", "").replace(")", "")
    return pd.to_numeric(text, errors="coerce")


def _parse_gb_from_text(text: str) -> int:
    """Extract the first '<number>GB' occurrence as integer GB."""
    if not isinstance(text, str):
        return 0
    m = re.search(r"(\d+)\s*GB", text, flags=re.IGNORECASE)
    return int(m.group(1)) if m else 0


def _parse_storage_gb_and_type(text: str) -> tuple[int, str]:
    """Extract storage size (GB/TB) + storage type (SSD/HDD) from text."""
    if not isinstance(text, str):
        return 0, "unknown"

    tb_match = re.search(r"(\d+)\s*TB", text, flags=re.IGNORECASE)
    gb_match = re.search(r"(\d+)\s*GB", text, flags=re.IGNORECASE)

    storage_gb = 0
    if tb_match:
        storage_gb = int(tb_match.group(1)) * 1024
    elif gb_match:
        storage_gb = int(gb_match.group(1))

    lowered = text.lower()
    storage_type = "HDD"
    if "ssd" in lowered or "nvme" in lowered or "flash" in lowered:
        storage_type = "SSD"
    elif "hdd" in lowered:
        storage_type = "HDD"

    return storage_gb, storage_type


def _parse_cpu_score(text: str) -> int:
    """
    Rough CPU tier for filtering/sorting:
    - Intel: Core i3/i5/i7/i9 => 3/5/7/9
    - AMD: Ryzen 3/5/7/9 => 3/5/7/9
    """
    if not isinstance(text, str):
        return 0
    m_intel = re.search(r"\b[iI]\s*(3|5|7|9)\s*-\d", text)
    if m_intel:
        return int(m_intel.group(1))
    m_ryzen = re.search(r"\bRyzen\s*(3|5|7|9)\b", text, flags=re.IGNORECASE)
    if m_ryzen:
        return int(m_ryzen.group(1))
    return 0


def _parse_gpu_score(text: str) -> int:
    """Rough GPU tier for sorting: RTX/GTX/RX models (best-effort)."""
    if not isinstance(text, str):
        return 0
    lowered = text.lower()
    # RTX 3060 -> 3060, RX 6600 -> 6600, GTX 1660 -> 1660
    m = re.search(r"\b(rtx|gtx|rx)\s*(\d{4}|\d{3})\b", lowered)
    if m:
        try:
            return int(m.group(2))
        except ValueError:
            return 0
    return 0


newegg_raw = pd.read_csv(DATA_DIR / "newegg.csv", encoding="latin1")
newegg_raw.columns = [c.strip() for c in newegg_raw.columns]

# Normalize category values (the dataset has small typos like `storege`, `moniter`).
newegg_raw["Category"] = newegg_raw["Category"].astype(str).str.strip().str.lower()
newegg_raw["price_sgd"] = _newegg_clean_numeric(newegg_raw["prices"]) * USD_TO_SGD
newegg_raw["rating_num"] = _newegg_clean_numeric(newegg_raw["ratings"])

newegg_raw["brand"] = newegg_raw["brand_name"].astype(str)
newegg_raw["item_desc"] = newegg_raw["items_Decribtion"].astype(str)

newegg_raw = newegg_raw.dropna(subset=["price_sgd"])

desktop_cpu_inventory = newegg_raw[newegg_raw["Category"] == "cpu"].copy()
desktop_cpu_inventory["cpu_score"] = desktop_cpu_inventory["item_desc"].apply(_parse_cpu_score)

desktop_ram_inventory = newegg_raw[newegg_raw["Category"] == "ram"].copy()
desktop_ram_inventory["ram_gb"] = desktop_ram_inventory["item_desc"].apply(_parse_gb_from_text)

desktop_storage_inventory = newegg_raw[newegg_raw["Category"] == "storege"].copy()
desktop_storage_inventory[["storage_gb", "storage_type"]] = desktop_storage_inventory["item_desc"].apply(
    lambda s: pd.Series(_parse_storage_gb_and_type(s))
)

desktop_gpu_inventory = newegg_raw[newegg_raw["Category"] == "gpu"].copy()
desktop_gpu_inventory["gpu_score"] = desktop_gpu_inventory["item_desc"].apply(_parse_gpu_score)

# Optional extras (only shown if the user explicitly asks).
desktop_monitor_inventory = newegg_raw[newegg_raw["Category"] == "moniter"].copy()
desktop_power_inventory = newegg_raw[newegg_raw["Category"] == "power"].copy()
desktop_motherboard_inventory = newegg_raw[newegg_raw["Category"] == "motherboard"].copy()


def _has_word(haystack: str, word: str) -> bool:
    """Whole-word match (avoids 'ai' in 'plain', 'ml' inside unrelated tokens)."""
    if not word or not haystack:
        return False
    return bool(re.search(rf"\b{re.escape(word)}\b", haystack))


def _parse_k_sgd_budget(text_lower: str) -> int | None:
    """e.g. 1.5k → 1500; skips '4k monitor' style resolution phrases."""
    m = re.search(
        r"\b(\d+(?:\.\d+)?)\s*k\b(?!\s*(?:monitor|display|screen|tv|panel|hdr|uhd|oled))",
        text_lower,
    )
    if not m:
        return None
    return int(float(m.group(1)) * 1000)


_MAX_UNITS_ORDERED = 500
_MAX_BUDGET_SGD = 400_000


def _finalize_requirements(req: dict, text_lower: str) -> None:
    """Caps and small contradiction fixes so downstream matching stays sane."""
    q = req.get("quantity", 1)
    if not isinstance(q, int) or q < 1:
        req["quantity"] = 1
    elif q > _MAX_UNITS_ORDERED:
        req["quantity"] = _MAX_UNITS_ORDERED

    b = req.get("budget")
    if b is not None:
        try:
            b_int = int(b)
        except (TypeError, ValueError):
            req["budget"] = None
        else:
            if b_int < 50:
                req["budget"] = None
            elif b_int > _MAX_BUDGET_SGD:
                req["budget"] = _MAX_BUDGET_SGD
            else:
                req["budget"] = b_int

    # Galaxy Tab is a tablet, not a phone, unless they also ask for a phone explicitly.
    if (
        "galaxy tab" in text_lower
        or re.search(r"\bgalaxy\s+tab\b", text_lower)
        or "tab s8" in text_lower
        or "tab s9" in text_lower
        or "tab s6" in text_lower
        or "tab a" in text_lower
    ):
        req["wants_tablet"] = True
        phone_markers = (
            "phone",
            "smartphone",
            "iphone",
            "cellular",
            "android phone",
            "galaxy s",
            "galaxy z",
        )
        if not any(m in text_lower for m in phone_markers):
            req["wants_phone"] = False


# ---------- 2. NLP parsing ----------
def parse_requirements(text: str) -> dict:
    """Parse free-text user requirements into structured fields."""
    if text is None:
        text = ""
    elif not isinstance(text, str):
        text = str(text)
    text_lower = text.lower()

    # Simple typo normalisation for a few key words
    typo_map = {
        "ipone": "iphone",
        "iphon": "iphone",
        "ifone": "iphone",
        "labtop": "laptop",
        "lapotp": "laptop",
        "latop": "laptop",
        "laptp": "laptop",
        "keybord": "keyboard",
        "keybard": "keyboard",
        "andriod": "android",
        "andorid": "android",
        "andorjd": "android",
        "ipdad": "ipad",
        "ipda": "ipad",
        "desktp": "desktop",
        "grafics": "graphics",
        "gamin": "gaming",
    }
    for wrong, correct in typo_map.items():
        text_lower = text_lower.replace(wrong, correct)

    # Quantity (not used directly in filtering, but useful for totals)
    # Capture phrases like "3 laptops", "2 tablets", "1 ipad", and "for 2"
    qty_pattern_items = re.findall(
        r"(\d+)\s*(laptop|notebook|desktop|desktops|pc|computer|computers|laptops|ipad|ipads|tablet|tablets|phone|phones|smartphone|smartphones|mobile|mobiles|tower|towers)",
        text_lower,
    )
    qty_pattern_for = re.findall(r"for\s+(\d+)\b", text_lower)
    qty_pattern_need = re.findall(r"need\s+(\d+)\b", text_lower)

    # Derive quantity: prefer explicit "3 laptops" etc., else "for 2" / "need 2", else 1
    if qty_pattern_items:
        quantity = int(qty_pattern_items[0][0])
    elif qty_pattern_for:
        quantity = int(qty_pattern_for[0])
    elif qty_pattern_need:
        quantity = int(qty_pattern_need[0])
    else:
        quantity = 1

    # For budget parsing, remove ALL quantity numbers from the text so that
    # they are not misinterpreted as a budget (e.g. "1 ipad" or "need 2" → not budget=1/2)
    text_for_budget = text_lower
    for num, _ in qty_pattern_items:
        text_for_budget = re.sub(rf"\b{num}\b", "", text_for_budget)
    for num in qty_pattern_for:
        text_for_budget = re.sub(rf"\b{num}\b", "", text_for_budget)
    for num in qty_pattern_need:
        text_for_budget = re.sub(rf"\b{num}\b", "", text_for_budget)

    # Also remove numbers that are clearly part of iPhone model names,
    # e.g. "iphone 13", "iphone 14", so they are not treated as budgets.
    iphone_model_nums = re.findall(r"iphone\s+(\d+)", text_for_budget)
    for num in iphone_model_nums:
        text_for_budget = re.sub(rf"\b{num}\b", "", text_for_budget)

    # Strip storage sizes so "512GB SSD" is not parsed as budget 512
    text_for_budget = re.sub(
        r"\b\d{1,4}\s*(?:gb|tb)\b",
        " ",
        text_for_budget,
        flags=re.IGNORECASE,
    )
    # Refresh / panel specs (avoid "144" in "144hz" becoming a budget)
    text_for_budget = re.sub(
        r"\b\d{2,3}\s*hz\b",
        " ",
        text_for_budget,
        flags=re.IGNORECASE,
    )
    text_for_budget = re.sub(
        r"\b\d{1,2}(?:\.\d+)?\s*(?:inch|inches)\b",
        " ",
        text_for_budget,
        flags=re.IGNORECASE,
    )

    def _normalize_money_num(s: str) -> int:
        return int(str(s).replace(",", "").replace(" ", ""))

    # Budget: under/budget/up-to/max/S$, then 1.5k-style, then a cautious standalone number
    budget = None
    budget_pattern = (
        r"(?:under|below|budget(?:\s+of)?|around|about|approx(?:imately)?|less\s+than|"
        r"up\s*to|upto|at\s+most|max(?:imum)?|cap)\s*(?:sgd|\$)?\s*([\d,]+(?:\.\d+)?)"
        r"|(?:sgd|\$)\s*([\d,]+(?:\.\d+)?)"
    )
    budget_match = re.search(budget_pattern, text_for_budget, flags=re.IGNORECASE)
    if budget_match:
        raw_amt = next(g for g in budget_match.groups() if g)
        end = budget_match.end()
        remainder = text_for_budget[end:].lstrip().lower()
        base = float(str(raw_amt).replace(",", ""))
        if remainder.startswith("k"):
            budget = int(base * 1000)
        else:
            budget = int(base)
    if budget is None:
        k_amt = _parse_k_sgd_budget(text_for_budget)
        if k_amt is not None:
            budget = k_amt
    if budget is None:
        loose_match = re.search(
            r"(?:^|\s)\$?\s*([\d,]+(?:\.\d+)?)(\s*k\b)?",
            text_for_budget,
            flags=re.IGNORECASE,
        )
        if loose_match:
            base = float(str(loose_match.group(1)).replace(",", ""))
            if loose_match.group(2):
                base *= 1000
            candidate = int(base)
            if quantity is not None and candidate == quantity:
                budget = None
            elif candidate < 100:
                budget = None
            else:
                budget = candidate

    # OS preference
    if "mac" in text_lower or "macos" in text_lower:
        os_pref = "mac"
    elif "windows" in text_lower or "win11" in text_lower or "win 11" in text_lower:
        os_pref = "windows"
    elif "linux" in text_lower or "ubuntu" in text_lower or "fedora" in text_lower:
        os_pref = "linux"
    else:
        os_pref = "any"

    # Job function / use-case (order matters: creative before video so "photo editing" is not
    # classified as video; gaming before student for "student gamer" queries.)
    if (
        "photoshop" in text_lower
        or "lightroom" in text_lower
        or "photo" in text_lower
        or "graphic design" in text_lower
        or "designer" in text_lower
        or "design work" in text_lower
        or "illustrator" in text_lower
        or "canva" in text_lower
        or "figma" in text_lower
        or "indesign" in text_lower
        or "cad" in text_lower
        or "autocad" in text_lower
        or "solidworks" in text_lower
    ):
        job = "creative_design"
    elif (
        "premiere" in text_lower
        or "after effects" in text_lower
        or "davinci" in text_lower
        or "final cut" in text_lower
        or "filmmaking" in text_lower
        or "video production" in text_lower
        or (
            "video" in text_lower
            and (
                "edit" in text_lower
                or "editing" in text_lower
                or "encoder" in text_lower
            )
        )
        or "twitch" in text_lower
        or "vlogger" in text_lower
        or "youtuber" in text_lower
        or (
            _has_word(text_lower, "obs")
            and ("stream" in text_lower or "recording" in text_lower or "broadcast" in text_lower)
        )
    ):
        job = "video_editing"
    elif (
        _has_word(text_lower, "account")
        or _has_word(text_lower, "accountant")
        or "accounting" in text_lower
        or "finance" in text_lower
        or "bookkeep" in text_lower
        or _has_word(text_lower, "excel")
        or "spreadsheets" in text_lower
        or "quickbooks" in text_lower
        or "xero" in text_lower
    ):
        job = "accounting"
    elif (
        "data science" in text_lower
        or "machine learning" in text_lower
        or "deep learning" in text_lower
        or "neural net" in text_lower
        or "jupyter" in text_lower
        or "pandas" in text_lower
        or "tensorflow" in text_lower
        or "pytorch" in text_lower
        or "scikit" in text_lower
        or "power bi" in text_lower
        or "tableau" in text_lower
        or _has_word(text_lower, "analytics")
        or _has_word(text_lower, "statistics")
        or _has_word(text_lower, "sql")
        or _has_word(text_lower, "ml")
        or _has_word(text_lower, "etl")
        or _has_word(text_lower, "ai")
    ):
        job = "data_science"
    elif (
        "developer" in text_lower
        or "coding" in text_lower
        or _has_word(text_lower, "code")
        or "programming" in text_lower
        or "software engineer" in text_lower
        or "web dev" in text_lower
        or "python" in text_lower
        or "java " in text_lower
        or "c++" in text_lower
        or "javascript" in text_lower
        or "typescript" in text_lower
        or "vscode" in text_lower
        or "visual studio" in text_lower
        or "github" in text_lower
        or "docker" in text_lower
        or "kubernetes" in text_lower
        or _has_word(text_lower, "devops")
        or "frontend" in text_lower
        or "backend" in text_lower
        or "full stack" in text_lower
        or "fullstack" in text_lower
        or "mobile app" in text_lower
        or "web app" in text_lower
        or "android app" in text_lower
        or "ios app" in text_lower
    ):
        job = "software_dev"
    elif (
        "gaming" in text_lower
        or "games" in text_lower
        or "gamer" in text_lower
        or "gamers" in text_lower
        or _has_word(text_lower, "game")
        or "valorant" in text_lower
        or "dota" in text_lower
        or "csgo" in text_lower
        or "counter-strike" in text_lower
        or "league of legends" in text_lower
        or "fortnite" in text_lower
        or "minecraft" in text_lower
        or "steam" in text_lower
        or "fps" in text_lower
        or "esports" in text_lower
    ):
        job = "gaming"
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
    else:
        job = "general_office"

    # Core device type: treat "pc/computer" as desktop unless "laptop/notebook" is mentioned.
    wants_laptop = (
        ("laptop" in text_lower)
        or ("notebook" in text_lower)
        or ("macbook" in text_lower)
        or ("chromebook" in text_lower)
        or ("ultrabook" in text_lower)
        or ("surface laptop" in text_lower)
    )
    pc_like = ("pc" in text_lower) or ("computer" in text_lower) or ("computers" in text_lower)
    wants_desktop = (
        ("desktop" in text_lower)
        or ("tower" in text_lower)
        or ("workstation" in text_lower)
        or (pc_like and not wants_laptop)
    )
    wants_mouse = "mouse" in text_lower or "mice" in text_lower
    wants_keyboard = "keyboard" in text_lower or "keycaps" in text_lower
    wants_phone = (
        "phone" in text_lower
        or "smartphone" in text_lower
        or "iphone" in text_lower
        or "galaxy" in text_lower
        or _has_word(text_lower, "pixel")
        or _has_word(text_lower, "oneplus")
        or _has_word(text_lower, "xiaomi")
    )
    wants_tablet = (
        "tablet" in text_lower
        or "ipad" in text_lower
        or (
            "surface" in text_lower
            and "surface laptop" not in text_lower
            and not wants_laptop
        )
    )

    req = {
        "job_function": job,
        "budget": budget,
        "quantity": quantity,
        "os_pref": os_pref,
        "wants_mouse": wants_mouse,
        "wants_keyboard": wants_keyboard,
        "wants_phone": wants_phone,
        "wants_tablet": wants_tablet,
        "wants_laptop": wants_laptop,
        "wants_desktop": wants_desktop,
        "raw_text": text,
    }
    _finalize_requirements(req, text_lower)
    return req


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
def _recommend_mice(req: dict, top_k: int = 3) -> pd.DataFrame:
    """Recommend gaming mice when the user asks for a mouse."""
    if not req.get("wants_mouse"):
        return mouse_inventory.head(0)  # empty with correct columns

    candidates = mouse_inventory.copy()

    raw_text = req.get("raw_text", "").lower()

    # Size preference (small / medium / large / fingertip)
    size_pref = None
    if "small mouse" in raw_text or "small size" in raw_text:
        size_pref = "Small"
    elif "large mouse" in raw_text or "large size" in raw_text:
        size_pref = "Large"
    elif "medium mouse" in raw_text or "medium size" in raw_text:
        size_pref = "Medium"
    elif "fingertip" in raw_text:
        size_pref = "Fingertip"
    if size_pref:
        candidates = candidates[candidates["size"].str.contains(size_pref, na=False)]

    # Connectivity preference (wired / wireless / bluetooth)
    if "wireless" in raw_text:
        candidates = candidates[candidates["connectivity"].str.contains("Wireless", na=False)]
    elif "wired" in raw_text or "cable" in raw_text:
        candidates = candidates[candidates["connectivity"].str.contains("Wired", na=False)]
    elif "bluetooth" in raw_text:
        candidates = candidates[candidates["connectivity"].str.contains("Bluetooth", na=False)]

    # DPI preference – look for explicit "<number> dpi" or phrases like "high dpi"
    min_dpi = None
    m = re.search(r"(\d+)\s*dpi", raw_text)
    if m:
        min_dpi = int(m.group(1))
    elif "high dpi" in raw_text or "fps games" in raw_text or "fps mouse" in raw_text:
        min_dpi = 12000
    if min_dpi:
        candidates = candidates[candidates["dpi"] >= min_dpi]

    # For gaming-heavy use, also prefer higher DPI / polling and lighter weight
    if req["job_function"] == "gaming":
        candidates = candidates[
            (candidates["dpi"] >= 12000) & (candidates["polling_hz"] >= 1000)
        ]

    candidates = candidates.sort_values(
        ["dpi", "polling_hz", "weight_g"],
        ascending=[False, False, True],
    )
    return candidates.head(top_k)


def _recommend_keyboards(req: dict, top_k: int = 3) -> pd.DataFrame:
    """Recommend keyboards when the user asks for a keyboard."""
    if not req.get("wants_keyboard"):
        return keyboard_inventory.head(0)

    candidates = keyboard_inventory.copy()

    raw_text = req.get("raw_text", "").lower()

    # Connection preference (wireless / bluetooth / usb)
    if "wireless" in raw_text:
        candidates = candidates[candidates["connection"].str.contains("Wireless", na=False)]
    elif "bluetooth" in raw_text:
        candidates = candidates[candidates["connection"].str.contains("Bluetooth", na=False)]
    elif "usb" in raw_text or "wired" in raw_text:
        candidates = candidates[candidates["connection"].str.contains("USB", na=False)]

    # For typing / office / dev, prefer:
    # - if user says "expensive" / "premium": higher price first
    # - otherwise: higher rating and more votes
    if "expensive" in raw_text or "premium" in raw_text or "high end" in raw_text:
        candidates = candidates.sort_values(
            ["price_sgd"], ascending=[False]
        )
    else:
        candidates = candidates.sort_values(
            ["rating", "votes"], ascending=[False, False]
        )
    return candidates.head(top_k)


def _recommend_phones(req: dict, top_k: int = 3) -> pd.DataFrame:
    """Recommend phones when the user asks for a phone."""
    if not req.get("wants_phone"):
        return phone_inventory.head(0)

    candidates = phone_inventory.copy()

    raw_text = req.get("raw_text", "").lower()

    # Brand / platform preference: iPhone vs Android brands
    if "iphone" in raw_text or "ios" in raw_text or "apple" in raw_text:
        candidates = candidates[candidates["brand"].str.contains("Apple", na=False)]
    elif "samsung" in raw_text:
        candidates = candidates[candidates["brand"].str.contains("Samsung", na=False)]
    elif "oneplus" in raw_text:
        candidates = candidates[candidates["brand"].str.contains("OnePlus", na=False)]

    # Apply budget if provided (budget is in SGD)
    if req["budget"]:
        candidates = candidates[candidates["price_sgd"] <= req["budget"]]

    # If the user mentions a specific iPhone model number / variant,
    # try to prioritise matching models first (e.g. "iphone 12 mini").
    if "iphone" in raw_text:
        # crude extraction: look for number after iphone
        m = re.search(r"iphone\s+(\d+)", raw_text)
        model_num = m.group(1) if m else None
        wants_mini = "mini" in raw_text
        if model_num:
            mask = candidates["model"].str.contains(model_num, case=False, na=False)
            if wants_mini:
                mask = mask & candidates["model"].str.contains("mini", case=False, na=False)
            filtered = candidates[mask]
            if not filtered.empty:
                candidates = filtered

    # For gaming / heavy use, prefer more RAM and battery;
    # otherwise prefer price, with optional "expensive" flag.
    if req["job_function"] in {"gaming", "video_editing", "data_science"}:
        candidates = candidates.sort_values(
            ["ram_gb", "battery_mah", "price_sgd"],
            ascending=[False, False, True],
        )
    else:
        if "expensive" in raw_text or "premium" in raw_text or "high end" in raw_text:
            candidates = candidates.sort_values(
                ["price_sgd"], ascending=[False]
            )
        else:
            candidates = candidates.sort_values(
                ["price_sgd"], ascending=[True]
            )

    return candidates.head(top_k)


def _recommend_ipads(req: dict, top_k: int = 3) -> pd.DataFrame:
    """Recommend iPads (tablets) when the user asks for a tablet/iPad."""
    if not req.get("wants_tablet"):
        return ipad_inventory.head(0)

    candidates = ipad_inventory.copy()

    # If the user mentions education, restrict to education-related segment
    raw_text_lower = req.get("raw_text", "").lower()
    if "education" in raw_text_lower or "student" in raw_text_lower or "school" in raw_text_lower:
        candidates = candidates[candidates["segment"].str.contains("Education", na=False)]

    # Apply budget if provided (budget is in SGD)
    if req["budget"]:
        candidates = candidates[candidates["price_sgd"] <= req["budget"]]

    raw = req.get("raw_text", "").lower()
    # Sort:
    # - if "expensive"/"premium": highest price first
    # - else: higher rating then lower price
    if "expensive" in raw or "premium" in raw or "high end" in raw:
        candidates = candidates.sort_values(
            ["price_sgd"], ascending=[False]
        )
    else:
        candidates = candidates.sort_values(
            ["rating", "price_sgd"], ascending=[False, True]
        )

    return candidates.head(top_k)


def _recommend_desktop_components(req: dict, top_k: int = 3) -> dict[str, pd.DataFrame]:
    """
    Recommend desktop build parts from `newegg.csv`.
    - CPU, RAM, Storage are always considered for desktop.
    - GPU is included when `job_to_min_specs(...).needs_gpu` is True.

    Returns a dict of DataFrames: { "cpu": ..., "ram": ..., "storage": ..., "gpu": ... }.
    """
    empty_cpu = desktop_cpu_inventory.head(0)
    empty_ram = desktop_ram_inventory.head(0)
    empty_storage = desktop_storage_inventory.head(0)
    empty_gpu = desktop_gpu_inventory.head(0)

    if not req.get("wants_desktop"):
        return {
            "cpu": empty_cpu,
            "ram": empty_ram,
            "storage": empty_storage,
            "gpu": empty_gpu,
        }

    spec = job_to_min_specs(req["job_function"])
    raw = req.get("raw_text", "").lower()
    expensive = "expensive" in raw or "premium" in raw or "high end" in raw

    def _sort_candidates(df: pd.DataFrame, include_rating: bool = True) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        if include_rating:
            df["rating_num_filled"] = df["rating_num"].fillna(0)
            if expensive:
                return df.sort_values(["price_sgd"], ascending=False)
            return df.sort_values(["rating_num_filled", "price_sgd"], ascending=[False, True])
        if expensive:
            return df.sort_values(["price_sgd"], ascending=False)
        return df.sort_values(["price_sgd"], ascending=True)

    def _apply_budget(df: pd.DataFrame, cap: float) -> pd.DataFrame:
        if df.empty or cap is None:
            return df
        filtered = df[df["price_sgd"] <= cap]
        return filtered if not filtered.empty else df

    total_budget = req.get("budget")

    # CPU
    cpu_candidates = desktop_cpu_inventory.copy()
    # Prefer mid/high-tier CPUs for heavier workloads.
    min_cpu_score = 5 if spec["needs_gpu"] else 0
    cpu_candidates = cpu_candidates[cpu_candidates["cpu_score"] >= min_cpu_score] if min_cpu_score else cpu_candidates
    if total_budget:
        cpu_candidates = _apply_budget(cpu_candidates, cap=total_budget * 0.25)
    cpu_candidates = _sort_candidates(cpu_candidates, include_rating=True).head(top_k)

    # RAM
    ram_candidates = desktop_ram_inventory.copy()
    ram_candidates = ram_candidates[ram_candidates["ram_gb"] >= spec["min_ram"]]
    if ram_candidates.empty:
        ram_candidates = desktop_ram_inventory.copy()
    if total_budget:
        ram_candidates = _apply_budget(ram_candidates, cap=total_budget * 0.20)
    ram_candidates = _sort_candidates(ram_candidates, include_rating=True).head(top_k)

    # Storage
    storage_candidates = desktop_storage_inventory.copy()
    storage_candidates = storage_candidates[storage_candidates["storage_gb"] >= spec["min_storage"]]
    if storage_candidates.empty:
        storage_candidates = desktop_storage_inventory.copy()
    if total_budget:
        storage_candidates = _apply_budget(storage_candidates, cap=total_budget * 0.25)
    storage_candidates = _sort_candidates(storage_candidates, include_rating=True).head(top_k)

    # GPU (optional)
    if spec["needs_gpu"]:
        gpu_candidates = desktop_gpu_inventory.copy()
        gpu_candidates = _sort_candidates(gpu_candidates, include_rating=True).head(top_k)
        if total_budget:
            gpu_candidates = _apply_budget(gpu_candidates, cap=total_budget * 0.30)
            if gpu_candidates.empty:
                gpu_candidates = desktop_gpu_inventory.copy()
                gpu_candidates = _apply_budget(gpu_candidates, cap=total_budget * 0.30)
                gpu_candidates = _sort_candidates(gpu_candidates, include_rating=True).head(top_k)
    else:
        gpu_candidates = empty_gpu

    return {
        "cpu": cpu_candidates,
        "ram": ram_candidates,
        "storage": storage_candidates,
        "gpu": gpu_candidates,
    }


def _select_laptops(req: dict, spec: dict, top_k: int) -> tuple[pd.DataFrame, str | None]:
    """Pick laptops with tiered relaxation (budget / dedicated GPU) and optional user-facing note."""
    raw = req.get("raw_text", "").lower()
    budget = req.get("budget")

    def _sort(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        if "expensive" in raw or "premium" in raw or "high end" in raw:
            return df.sort_values("price_sgd", ascending=False)
        return df.sort_values("price_sgd", ascending=True)

    def _apply_os(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        if req["os_pref"] == "mac":
            return df[df["brand"] == "Apple"]
        if req["os_pref"] in ("windows", "linux"):
            return df[df["brand"] != "Apple"]
        return df

    def _build(*, use_budget: bool, dedicated_gpu_only: bool) -> pd.DataFrame:
        df = laptop_inventory[
            (laptop_inventory["ram_gb"] >= spec["min_ram"])
            & (laptop_inventory["storage_gb"] >= spec["min_storage"])
        ]
        if dedicated_gpu_only:
            df = df[df["gpu_type"] == "dedicated"]
        if use_budget and budget:
            df = df[df["price_sgd"] <= budget]
        df = _apply_os(df)
        if df.empty:
            return df
        return _sort(df)

    full = _build(use_budget=True, dedicated_gpu_only=spec["needs_gpu"])
    if not full.empty:
        return full.head(top_k), None

    if budget:
        relaxed = _build(use_budget=False, dedicated_gpu_only=spec["needs_gpu"])
        if not relaxed.empty:
            return relaxed.head(top_k), (
                "No laptops matched under your budget; showing the best spec fits "
                "without a price cap."
            )

    if spec["needs_gpu"]:
        mid = _build(use_budget=True, dedicated_gpu_only=False)
        if not mid.empty:
            return mid.head(top_k), (
                "No dedicated-GPU laptops matched your filters; showing strong "
                "integrated-GPU options instead."
            )
        if budget:
            mid2 = _build(use_budget=False, dedicated_gpu_only=False)
            if not mid2.empty:
                return mid2.head(top_k), (
                    "Relaxed GPU and budget to still show useful laptop options."
                )

    return laptop_inventory.head(0), None


def recommend_devices(user_text: str, top_k: int = 3):
    """Return parsed requirements and top matching laptops (and mice) from inventory."""
    req = parse_requirements(user_text)
    spec = job_to_min_specs(req["job_function"])
    req.pop("assistant_note", None)

    # Only recommend core devices when the user asks for them explicitly,
    # otherwise fall back to laptops if they didn't specify any accessories.
    wants_any_accessory = (
        req.get("wants_mouse")
        or req.get("wants_keyboard")
        or req.get("wants_phone")
        or req.get("wants_tablet")
    )
    wants_laptop = req.get("wants_laptop", False)
    wants_desktop = req.get("wants_desktop", False)

    if wants_laptop or (not wants_desktop and not wants_any_accessory):
        laptop_candidates, lap_note = _select_laptops(req, spec, top_k)
        if lap_note:
            req["assistant_note"] = lap_note
    else:
        laptop_candidates = laptop_inventory.head(0)

    desktop_candidates = _recommend_desktop_components(req, top_k=top_k)

    # Mouse recommendations disabled (dataset has no prices and mouse flow removed)
    mouse_candidates = mouse_inventory.head(0)
    keyboard_candidates = _recommend_keyboards(req, top_k=top_k)
    phone_candidates = _recommend_phones(req, top_k=top_k)
    ipad_candidates = _recommend_ipads(req, top_k=top_k)

    return (
        req,
        laptop_candidates,
        desktop_candidates,
        mouse_candidates,
        keyboard_candidates,
        phone_candidates,
        ipad_candidates,
    )


def format_reply(
    req: dict,
    laptop_candidates: pd.DataFrame,
    desktop_candidates: dict[str, pd.DataFrame],
    mouse_candidates: pd.DataFrame,
    keyboard_candidates: pd.DataFrame,
    phone_candidates: pd.DataFrame,
    ipad_candidates: pd.DataFrame,
) -> str:
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

    wants_any_accessory = (
        req.get("wants_mouse")
        or req.get("wants_keyboard")
        or req.get("wants_phone")
        or req.get("wants_tablet")
    )
    desktop_empty = (
        desktop_candidates is None
        or all(df.empty for df in desktop_candidates.values())
    )
    show_core_context = (not laptop_candidates.empty) or (not desktop_empty)

    lines = []
    if show_core_context:
        lines.append(
            f"{Fore.CYAN}Interpreted need:{Style.RESET_ALL} {job_label}"
        )
    lines.append(f"{Fore.CYAN}Quantity:{Style.RESET_ALL} {req['quantity']} device(s)")
    if req["budget"]:
        lines.append(
            f"{Fore.CYAN}Budget per device:{Style.RESET_ALL} about S${req['budget']}"
        )
    base_spec = job_to_min_specs(req["job_function"])
    if not laptop_candidates.empty:
        lines.append(
            f"{Fore.CYAN}Recommended minimum laptop specs:{Style.RESET_ALL} "
            f"{base_spec['min_ram']}GB RAM, "
            f"{base_spec['min_storage']}GB SSD, "
            f"{'dedicated GPU' if base_spec['needs_gpu'] else 'integrated GPU OK'}"
        )
    if not desktop_empty:
        lines.append(
            f"{Fore.CYAN}Recommended minimum desktop parts:{Style.RESET_ALL} "
            f"{base_spec['min_ram']}GB RAM, "
            f"{base_spec['min_storage']}GB SSD storage, "
            f"{'dedicated GPU required' if base_spec['needs_gpu'] else 'integrated OK'}"
        )
    lines.append("")

    if (
        laptop_candidates.empty
        and mouse_candidates.empty
        and desktop_empty
        and keyboard_candidates.empty
        and phone_candidates.empty
        and ipad_candidates.empty
    ):
        lines.append(
            f"{Fore.RED}No matching devices found in the current inventory for this budget/spec.{Style.RESET_ALL}"
        )
        return "\n".join(lines)

    if not laptop_candidates.empty:
        lines.append(
            f"{Fore.GREEN}Top matching laptops (SGD, approx):{Style.RESET_ALL}"
        )
        header = (
            f"{'#':<3} {'Brand':<12} {'Model':<24} "
            f"{'New':>8} {'Used':>8} {'Total (New)':>13}"
        )
        lines.append(header)
        lines.append("-" * len(header))
        for idx, (_, row) in enumerate(laptop_candidates.iterrows(), start=1):
            price_sgd = row["price_sgd"]
            total_price = price_sgd * req["quantity"]
            used_price = estimate_used_price(price_sgd)
            lines.append(
                f"{idx:<3} "
                f"{str(row['brand'])[:12]:<12} "
                f"{str(row['model'])[:24]:<24} "
                f"S${price_sgd:>6.0f} "
                f"S${used_price:>6.0f} "
                f"S${total_price:>11.0f}"
            )

    # Desktop build parts
    if not desktop_empty:
        desktop_any = False
        for key in ["cpu", "ram", "storage", "gpu"]:
            if key in desktop_candidates and not desktop_candidates[key].empty:
                desktop_any = True
                break

        if desktop_any:
            lines.append("")
            lines.append(f"{Fore.GREEN}Desktop build parts (SGD, approx):{Style.RESET_ALL}")

        # CPU
        cpu_df = desktop_candidates.get("cpu")
        if cpu_df is not None and not cpu_df.empty:
            header = f"{'#':<3} {'CPU/Brand':<40} {'New':>8} {'Used':>8}"
            lines.append("")
            lines.append(f"{Fore.CYAN}CPU candidates:{Style.RESET_ALL}")
            lines.append(header)
            lines.append("-" * len(header))
            for idx, (_, row) in enumerate(cpu_df.iterrows(), start=1):
                used_price = estimate_used_price(row["price_sgd"])
                item = f"{row['brand']} {row['item_desc']}"
                lines.append(
                    f"{idx:<3} {item[:40]:<40} "
                    f"S${row['price_sgd']:>6.0f} "
                    f"S${used_price:>6.0f}"
                )

        # RAM
        ram_df = desktop_candidates.get("ram")
        if ram_df is not None and not ram_df.empty:
            header = f"{'#':<3} {'RAM':<14} {'New':>8} {'Used':>8}"
            lines.append("")
            lines.append(f"{Fore.CYAN}RAM candidates (meets min RAM if possible):{Style.RESET_ALL}")
            lines.append(header)
            lines.append("-" * len(header))
            for idx, (_, row) in enumerate(ram_df.iterrows(), start=1):
                used_price = estimate_used_price(row["price_sgd"])
                ram_label = f"{int(row['ram_gb'])}GB"
                lines.append(
                    f"{idx:<3} {ram_label:<14} "
                    f"S${row['price_sgd']:>6.0f} "
                    f"S${used_price:>6.0f}"
                )

        # Storage
        storage_df = desktop_candidates.get("storage")
        if storage_df is not None and not storage_df.empty:
            header = f"{'#':<3} {'Storage':<16} {'New':>8} {'Used':>8}"
            lines.append("")
            lines.append(f"{Fore.CYAN}Storage candidates (meets min storage if possible):{Style.RESET_ALL}")
            lines.append(header)
            lines.append("-" * len(header))
            for idx, (_, row) in enumerate(storage_df.iterrows(), start=1):
                used_price = estimate_used_price(row["price_sgd"])
                storage_label = f"{int(row['storage_gb'])}GB {row['storage_type']}"
                lines.append(
                    f"{idx:<3} {storage_label:<16} "
                    f"S${row['price_sgd']:>6.0f} "
                    f"S${used_price:>6.0f}"
                )

        # GPU (optional)
        gpu_df = desktop_candidates.get("gpu")
        if gpu_df is not None and not gpu_df.empty:
            header = f"{'#':<3} {'GPU/Brand':<40} {'New':>8} {'Used':>8}"
            lines.append("")
            lines.append(f"{Fore.CYAN}GPU candidates (only when recommended):{Style.RESET_ALL}")
            lines.append(header)
            lines.append("-" * len(header))
            for idx, (_, row) in enumerate(gpu_df.iterrows(), start=1):
                used_price = estimate_used_price(row["price_sgd"])
                item = f"{row['brand']} {row['item_desc']}"
                lines.append(
                    f"{idx:<3} {item[:40]:<40} "
                    f"S${row['price_sgd']:>6.0f} "
                    f"S${used_price:>6.0f}"
                )

    # Mouse suggestions disabled

    if not keyboard_candidates.empty:
        lines.append("")
        # Keyboard preference summary
        kb_prefs = []
        raw = req.get("raw_text", "").lower()
        if "wireless" in raw:
            kb_prefs.append("wireless")
        elif "bluetooth" in raw:
            kb_prefs.append("Bluetooth")
        elif "usb" in raw or "wired" in raw:
            kb_prefs.append("USB / wired")
        if kb_prefs:
            lines.append(
                f"{Fore.CYAN}Keyboard preferences:{Style.RESET_ALL} "
                + ", ".join(kb_prefs)
            )
        lines.append(
            f"{Fore.GREEN}Suggested keyboards (SGD, approx):{Style.RESET_ALL}"
        )
        header = (
            f"{'#':<3} {'Name':<26} {'Conn':<10} "
            f"{'New':>8} {'Used':>8} {'Rating':>8}"
        )
        lines.append(header)
        lines.append("-" * len(header))
        for idx, (_, row) in enumerate(keyboard_candidates.iterrows(), start=1):
            conn = row["connection"] if isinstance(row["connection"], str) else "Unknown"
            rating_val = (
                f"{row['rating']:.1f}" if not pd.isna(row["rating"]) else "N/A"
            )
            used_price = estimate_used_price(row["price_sgd"])
            name = str(row["name"])[:26]
            lines.append(
                f"{idx:<3} {name:<26} "
                f"{str(conn)[:10]:<10} "
                f"S${row['price_sgd']:>6.0f} "
                f"S${used_price:>6.0f} "
                f"{rating_val:>8}"
            )

    if not phone_candidates.empty:
        lines.append("")
        # Phone preference summary
        phone_prefs = []
        raw = req.get("raw_text", "").lower()
        if "iphone" in raw or "ios" in raw or "apple" in raw:
            phone_prefs.append("Apple / iPhone")
        elif "samsung" in raw:
            phone_prefs.append("Samsung")
        elif "oneplus" in raw:
            phone_prefs.append("OnePlus")
        if "camera" in raw:
            phone_prefs.append("better camera")
        if "battery" in raw:
            phone_prefs.append("larger battery")
        if phone_prefs:
            lines.append(
                f"{Fore.CYAN}Phone preferences:{Style.RESET_ALL} "
                + ", ".join(phone_prefs)
            )
        lines.append(
            f"{Fore.GREEN}Suggested phones (per device, SGD, approx):{Style.RESET_ALL}"
        )
        header = (
            f"{'#':<3} {'Brand':<10} {'Model':<20} "
            f"{'RAM':<5} {'Storage':<8} {'New':>8} {'Used':>8}"
        )
        lines.append(header)
        lines.append("-" * len(header))
        for idx, (_, row) in enumerate(phone_candidates.iterrows(), start=1):
            used_price = estimate_used_price(row["price_sgd"])
            lines.append(
                f"{idx:<3} "
                f"{str(row['brand'])[:10]:<10} "
                f"{str(row['model'])[:20]:<20} "
                f"{int(row['ram_gb']):<5} "
                f"{int(row['storage_gb']):<8} "
                f"S${row['price_sgd']:>6.0f} "
                f"S${used_price:>6.0f}"
            )

    if not ipad_candidates.empty:
        lines.append("")
        # iPad / tablet preference summary
        ipad_prefs = []
        raw = req.get("raw_text", "").lower()
        if "education" in raw or "student" in raw or "school" in raw:
            ipad_prefs.append("education / student segment")
        if ipad_prefs:
            lines.append(
                f"{Fore.CYAN}iPad / tablet preferences:{Style.RESET_ALL} "
                + ", ".join(ipad_prefs)
            )
        lines.append(
            f"{Fore.GREEN}Suggested iPads / tablets (per device, SGD, approx):{Style.RESET_ALL}"
        )
        header = (
            f"{'#':<3} {'Model':<24} {'Storage':<10} "
            f"{'New':>8} {'Used':>8}"
        )
        lines.append(header)
        lines.append("-" * len(header))
        for idx, (_, row) in enumerate(ipad_candidates.iterrows(), start=1):
            used_price = estimate_used_price(row["price_sgd"])
            lines.append(
                f"{idx:<3} "
                f"{str(row['product_name'])[:24]:<24} "
                f"{str(row['storage'])[:10]:<10} "
                f"S${row['price_sgd']:>6.0f} "
                f"S${used_price:>6.0f}"
            )

    return "\n".join(lines)


if __name__ == "__main__":
    print("Specs-to-Need Assistant (type 'exit' to quit)\n")
    try:
        while True:
            user_text = input(
                "Describe what you need (e.g. 'I need 3 laptops for video editing under 1500, plus a keyboard, phone and iPad'): "
            )
            if user_text.strip().lower() in {"exit", "quit"}:
                break
            (
                req,
                laptop_recs,
                desktop_recs,
                mouse_recs,
                keyboard_recs,
                phone_recs,
                ipad_recs,
            ) = recommend_devices(user_text)
            print()
            print(
                format_reply(
                    req,
                    laptop_recs,
                    desktop_recs,
                    mouse_recs,
                    keyboard_recs,
                    phone_recs,
                    ipad_recs,
                )
            )
            print("-" * 60)
    except KeyboardInterrupt:
        print("\nExiting assistant.")

