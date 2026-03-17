import re

import pandas as pd
from colorama import Fore, Style, init as colorama_init


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
laptop_raw = pd.read_csv("laptop_price.csv", encoding="latin1")

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
keyboard_raw = pd.read_csv("all_keyboards.csv", encoding="latin1")

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
phones_raw = pd.read_csv("Mobile phone price.csv", encoding="latin1")

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
ipad_raw = pd.read_csv("apple_global_sales_dataset.csv", encoding="latin1")

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


# ---------- 2. NLP parsing ----------
def parse_requirements(text: str) -> dict:
    """Parse free-text user requirements into structured fields."""
    text_lower = text.lower()

    # Simple typo normalisation for a few key words
    typo_map = {
        "ipone": "iphone",
        "iphon": "iphone",
        "ifone": "iphone",
        "labtop": "laptop",
        "lapotp": "laptop",
        "latop": "laptop",
        "andriod": "android",
        "andorid": "android",
        "andorjd": "android",
        "ipdad": "ipad",
        "ipda": "ipad",
    }
    for wrong, correct in typo_map.items():
        text_lower = text_lower.replace(wrong, correct)

    # Quantity (not used directly in filtering, but useful for totals)
    # Capture phrases like "3 laptops", "2 tablets", "1 ipad", and "for 2"
    qty_pattern_items = re.findall(
        r"(\d+)\s*(laptop|pc|computer|computers|laptops|ipad|ipads|tablet|tablets|phone|phones|smartphone|smartphones|mobile|mobiles)",
        text_lower,
    )
    qty_pattern_for = re.findall(r"for\s+(\d+)\b", text_lower)

    # Derive quantity: prefer explicit "3 laptops" etc., else "for 2", else 1
    if qty_pattern_items:
        quantity = int(qty_pattern_items[0][0])
    elif qty_pattern_for:
        quantity = int(qty_pattern_for[0])
    else:
        quantity = 1

    # For budget parsing, remove ALL quantity numbers from the text so that
    # they are not misinterpreted as a budget (e.g. "1 ipad" → not budget=1)
    text_for_budget = text_lower
    for num, _ in qty_pattern_items:
        text_for_budget = re.sub(rf"\b{num}\b", "", text_for_budget)
    for num in qty_pattern_for:
        text_for_budget = re.sub(rf"\b{num}\b", "", text_for_budget)

    # Also remove numbers that are clearly part of iPhone model names,
    # e.g. "iphone 13", "iphone 14", so they are not treated as budgets.
    iphone_model_nums = re.findall(r"iphone\s+(\d+)", text_for_budget)
    for num in iphone_model_nums:
        text_for_budget = re.sub(rf"\b{num}\b", "", text_for_budget)

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
            # also ignore obviously too-small "budgets" like 12 from "iphone 12"
            elif candidate < 100:
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
        or "app" in text_lower
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

    # Whether user explicitly wants a mouse and/or keyboard / phone / tablet as well
    wants_laptop = (
        "laptop" in text_lower
        or "pc" in text_lower
        or "computer" in text_lower
        or "computers" in text_lower
    )
    wants_mouse = "mouse" in text_lower or "mice" in text_lower
    wants_keyboard = "keyboard" in text_lower or "keycaps" in text_lower
    wants_phone = (
        "phone" in text_lower or "smartphone" in text_lower or "mobile" in text_lower
    )
    wants_tablet = "tablet" in text_lower or "ipad" in text_lower

    return {
        "job_function": job,
        "budget": budget,
        "quantity": quantity,
        "os_pref": os_pref,
        "wants_mouse": wants_mouse,
        "wants_keyboard": wants_keyboard,
        "wants_phone": wants_phone,
        "wants_tablet": wants_tablet,
        "wants_laptop": wants_laptop,
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


def recommend_devices(user_text: str, top_k: int = 3):
    """Return parsed requirements and top matching laptops (and mice) from inventory."""
    req = parse_requirements(user_text)
    spec = job_to_min_specs(req["job_function"])

    # Only recommend laptops if user asked for them explicitly OR
    # did not specify any other concrete device type.
    wants_any_non_laptop = (
        req.get("wants_mouse")
        or req.get("wants_keyboard")
        or req.get("wants_phone")
        or req.get("wants_tablet")
    )
    if req.get("wants_laptop") or not wants_any_non_laptop:
        laptop_candidates = laptop_inventory[
            (laptop_inventory["ram_gb"] >= spec["min_ram"])
            & (laptop_inventory["storage_gb"] >= spec["min_storage"])
        ]

        if spec["needs_gpu"]:
            laptop_candidates = laptop_candidates[
                laptop_candidates["gpu_type"] == "dedicated"
            ]

        # Budget filter (per device), interpreted as SGD
        if req["budget"]:
            laptop_candidates = laptop_candidates[
                laptop_candidates["price_sgd"] <= req["budget"]
            ]

        # OS preference
        if req["os_pref"] == "mac":
            laptop_candidates = laptop_candidates[
                laptop_candidates["brand"] == "Apple"
            ]
        elif req["os_pref"] == "windows":
            laptop_candidates = laptop_candidates[
                laptop_candidates["brand"] != "Apple"
            ]

        raw = req.get("raw_text", "").lower()
        # Sort:
        # - if "expensive"/"premium": highest price first
        # - else: lower price first
        if "expensive" in raw or "premium" in raw or "high end" in raw:
            laptop_candidates = laptop_candidates.sort_values(
                "price_sgd", ascending=False
            ).head(top_k)
        else:
            laptop_candidates = laptop_candidates.sort_values(
                "price_sgd", ascending=True
            ).head(top_k)
    else:
        laptop_candidates = laptop_inventory.head(0)
    # Mouse recommendations disabled (dataset has no prices and mouse flow removed)
    mouse_candidates = mouse_inventory.head(0)
    keyboard_candidates = _recommend_keyboards(req, top_k=top_k)
    phone_candidates = _recommend_phones(req, top_k=top_k)
    ipad_candidates = _recommend_ipads(req, top_k=top_k)

    return (
        req,
        laptop_candidates,
        mouse_candidates,
        keyboard_candidates,
        phone_candidates,
        ipad_candidates,
    )


def format_reply(
    req: dict,
    laptop_candidates: pd.DataFrame,
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

    wants_any_non_laptop = (
        req.get("wants_mouse")
        or req.get("wants_keyboard")
        or req.get("wants_phone")
        or req.get("wants_tablet")
    )
    show_laptop_context = req.get("wants_laptop") or not wants_any_non_laptop

    lines = []
    if show_laptop_context:
        lines.append(
            f"{Fore.CYAN}Interpreted need:{Style.RESET_ALL} {job_label}"
        )
    lines.append(f"{Fore.CYAN}Quantity:{Style.RESET_ALL} {req['quantity']} device(s)")
    if req["budget"]:
        lines.append(
            f"{Fore.CYAN}Budget per device:{Style.RESET_ALL} about S${req['budget']}"
        )
    # Only show laptop minimum specs when laptops are part of the recommendation
    if show_laptop_context:
        base_spec = job_to_min_specs(req["job_function"])
        lines.append(
            f"{Fore.CYAN}Recommended minimum laptop specs:{Style.RESET_ALL} "
            f"{base_spec['min_ram']}GB RAM, "
            f"{base_spec['min_storage']}GB SSD, "
            f"{'dedicated GPU' if base_spec['needs_gpu'] else 'integrated GPU OK'}"
        )
    lines.append("")

    if (
        laptop_candidates.empty
        and mouse_candidates.empty
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
            f"{Fore.GREEN}Top matching laptops (per device, prices in SGD, approx):{Style.RESET_ALL}"
        )
        for _, row in laptop_candidates.iterrows():
            price_sgd = row["price_sgd"]
            total_price = price_sgd * req["quantity"]
             # Simple 2nd-hand heuristic based on laptop price
            used_price = estimate_used_price(price_sgd)
            lines.append(
                f"{Fore.YELLOW}- ID {row['id']}{Style.RESET_ALL}: "
                f"{Fore.MAGENTA}{row['brand']} {row['model']}{Style.RESET_ALL} "
                f"({row['cpu']}, {row['ram_gb']}GB RAM, {row['storage_gb']}GB {row['storage_type']}, "
                f"GPU: {row['gpu_type']}), "
                f"{Fore.GREEN}Price per device (new-ish):{Style.RESET_ALL} S${price_sgd:.0f}, "
                f"{Fore.MAGENTA}suggested 2nd-hand:{Style.RESET_ALL} S${used_price:.0f}, "
                f"{Fore.GREEN}Estimated total for {req['quantity']} (new-ish):{Style.RESET_ALL} S${total_price:.0f}"
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
        lines.append(f"{Fore.GREEN}Suggested keyboards:{Style.RESET_ALL}")
        for _, row in keyboard_candidates.iterrows():
            conn = row["connection"] if isinstance(row["connection"], str) else "Unknown"
            rating_val = (
                f"{row['rating']:.1f}" if not pd.isna(row["rating"]) else "Unknown"
            )
            votes_val = int(row["votes"]) if not pd.isna(row["votes"]) else 0
            used_price = estimate_used_price(row["price_sgd"])
            lines.append(
                f"{Fore.YELLOW}- ID {row['id']}{Style.RESET_ALL}: "
                f"{Fore.MAGENTA}{row['name']}{Style.RESET_ALL} "
                f"({row['type']}, connection: {conn}, "
                f"approx new price: S${row['price_sgd']:.2f}, "
                f"suggested 2nd-hand: S${used_price:.2f}, "
                f"rating: {rating_val} "
                f"from {votes_val} votes)"
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
            f"{Fore.GREEN}Suggested phones (prices in SGD, approx):{Style.RESET_ALL}"
        )
        for _, row in phone_candidates.iterrows():
            used_price = estimate_used_price(row["price_sgd"])
            lines.append(
                f"{Fore.YELLOW}- ID {row['id']}{Style.RESET_ALL}: "
                f"{Fore.MAGENTA}{row['brand']} {row['model']}{Style.RESET_ALL} "
                f"(~S${row['price_sgd']:.0f}, "
                f"{row['ram_gb']:.0f}GB RAM, {row['storage_gb']:.0f}GB storage, "
                f"battery {row['battery_mah']:.0f}mAh, "
                f"rear cameras: {row['rear_cam_mp']}), "
                f"{Fore.MAGENTA}suggested 2nd-hand:{Style.RESET_ALL} S${used_price:.0f}"
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
            f"{Fore.GREEN}Suggested iPads / tablets (prices in SGD, approx):{Style.RESET_ALL}"
        )
        for _, row in ipad_candidates.iterrows():
            used_price = estimate_used_price(row["price_sgd"])
            lines.append(
                f"{Fore.YELLOW}- ID {row['id']}{Style.RESET_ALL}: "
                f"{Fore.MAGENTA}{row['product_name']}{Style.RESET_ALL} "
                f"({row['storage']}, color: {row['color']}, "
                f"approx new price: S${row['price_sgd']:.0f}, "
                f"suggested 2nd-hand: S${used_price:.0f}, "
                f"country: {row['country']}, year: {row['year']}, "
                f"segment: {row['segment']}, "
                f"rating: {row['rating'] if not pd.isna(row['rating']) else 'N/A'})"
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
                    mouse_recs,
                    keyboard_recs,
                    phone_recs,
                    ipad_recs,
                )
            )
            print("-" * 60)
    except KeyboardInterrupt:
        print("\nExiting assistant.")

