## Circular Economy for E‑Waste – Analytics & AI Prototype

This repository contains the **Python prototype** for a B2B circular marketplace that extends the life of corporate IT hardware and helps SMEs buy affordable, fit‑for‑purpose devices.

It demonstrates two core components of the platform:

1. **FMV (Fair Market Value) Pricing Engine** – estimates a fair resale price for used laptops based on specs and condition.  
2. **Specs‑to‑Need Assistant** – an AI‑style helper that translates business needs (in plain English) into hardware recommendations using a small inventory.

---

### 1. Project Structure

- `fmv_engine.py` – synthetic data + ML model that predicts fair market value for a device.
- `specs_to_need_bot.py` – simple NLP + rules to recommend devices from a sample inventory.
- `requirements.txt` – Python dependencies.

(Figma wireframes for the UI are kept separately in Figma and are referenced in the course presentation.)

---

### 2. Setup & Installation

**Prerequisites**

- Python 3.9+ installed
- `pip` available on your system

**Steps**

```bash
# 1. Clone this repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

# 2. Install dependencies
pip install -r requirements.txt
```

---

### 3. FMV Pricing Engine (`fmv_engine.py`)

**Goal**

Provide a *data‑driven* fair price estimate for a used enterprise laptop, based on:

- Brand, model, CPU
- RAM, storage size & type
- GPU type
- Age (in years)
- Battery health
- Cosmetic grade (A/B)

**Dataset structure**

Inside `fmv_engine.py`, a small synthetic dataset is defined as a list of rows, then converted to a DataFrame:

```python
data = [
    # brand, model, cpu, ram_gb, storage_gb, storage_type, gpu_type, age_years, battery_health, grade, price
    ["Dell", "Latitude 7420", "i5", 8, 256, "SSD", "integrated", 1, 95, "A", 950],
    ...
]

columns = [
    "brand",          # manufacturer, e.g. Dell, HP, Lenovo, Apple
    "model",          # specific model name, e.g. Latitude 7420
    "cpu",            # CPU family/chip, e.g. i5, i7, M1
    "ram_gb",         # RAM size in GB (8, 16, etc.)
    "storage_gb",     # storage size in GB (256, 512, 1000)
    "storage_type",   # storage type, e.g. SSD (could be HDD/SSD in bigger dataset)
    "gpu_type",       # graphics type: "integrated" or "dedicated"
    "age_years",      # how many years old the device is
    "battery_health", # battery condition as a percentage (0–100)
    "grade",          # cosmetic/overall grade, e.g. A or B
    "price",          # actual resale price in SGD (target for prediction)
]
```

- All columns **except `price`** are **input features** (`X`).  
- `price` is the **label** (`y`) the model learns to predict.

**Column meanings (plain English)**

- **`brand`** – laptop manufacturer (Dell, HP, Lenovo, Apple, etc.).  
- **`model`** – product line / model name (e.g. Latitude 7420, ThinkPad T14, MacBook Pro 13).  
- **`cpu`** – CPU family or chip (e.g. i5, i7, M1); higher‑end CPUs usually give better performance and value.  
- **`ram_gb`** – amount of RAM in gigabytes; higher RAM helps with multitasking and heavy apps.  
- **`storage_gb`** – internal storage size in gigabytes (how much data/apps you can store).  
- **`storage_type`** – type of storage drive; SSD is faster than HDD and usually more valuable.  
- **`gpu_type`** – `"integrated"` (built into CPU, good for office use) or `"dedicated"` (separate GPU, better for video editing/graphics).  
- **`age_years`** – how many years the device has been in use; older devices usually have lower resale value.  
- **`battery_health`** – battery condition as a percentage of original capacity (100% ≈ new, 80% = 80% of original).  
- **`grade`** – overall cosmetic/functional condition:  
  - **A‑grade**: very good condition, minimal wear, fully functional, higher value.  
  - **B‑grade**: visible but acceptable signs of use (scratches, small dents), still fully functional, slightly lower value.  
- **`price` (SGD)** – the resale price in Singapore dollars that the model is trying to predict from all the other columns.

**How it works**

1. The synthetic dataset above is loaded into a Pandas DataFrame.  
2. Categorical features are one‑hot encoded; numeric features are passed through.  
3. A `RandomForestRegressor` is trained inside an `sklearn` `Pipeline`.  
4. The function `predict_fmv(device_dict)` takes a Python `dict` describing one device and returns a predicted price.  
5. In `__main__`, the script predicts FMV for a sample device and prints the result.

**Run**

```bash
python fmv_engine.py
```

You’ll see a demo R² score plus a predicted FMV price printed to the console.

---

### 4. Specs‑to‑Need Assistant (`specs_to_need_bot.py`)

**Goal**

Act as a simple “virtual CTO” for non‑technical SME owners:

- User describes needs in plain English (e.g. “laptop for video editing under $1500”).  
- The bot infers the job type, budget, and OS preference.  
- It recommends suitable devices from a small inventory.

**Inventory dataset**

Inside `specs_to_need_bot.py`, the sample inventory looks like:

```python
inventory_data = [
    # id, brand, model, cpu, ram_gb, storage_gb, storage_type, gpu_type, price
    [1, "Dell", "Latitude 7420", "i5", 8, 256, "SSD", "integrated", 900],
    ...
]
```

Columns:

- `id` – internal ID of the listing  
- `brand`, `model`, `cpu` – device identity/specs  
- `ram_gb`, `storage_gb`, `storage_type` – performance‑related specs  
- `gpu_type` – `"integrated"` or `"dedicated"`  
- `price` – listing price in USD

**How it works**

1. **NLP parsing (`parse_requirements`)**
   - Uses regex and keyword checks to extract:
     - `budget` (first number in the text)
     - `quantity` (e.g. “3 laptops”)
     - `os_pref` (`mac`, `windows`, or `any`)
     - `job_function` (video editing, accounting, data science, software dev, or general office)
2. **Specs mapping (`job_to_min_specs`)**
   - Maps each `job_function` to minimum recommended specs, e.g.:
     - Video editing → 16GB RAM, 512GB SSD, dedicated GPU
     - Accounting → 8GB RAM, 256GB SSD, integrated GPU is fine
3. **Recommendation (`recommend_devices`)**
   - Filters the inventory by:
     - Minimum RAM and storage
     - GPU requirement
     - Budget per device
     - OS preference
   - Returns up to `top_k` cheapest matching devices.
4. **Formatting (`format_reply`)**
   - Generates a human‑readable explanation with:
     - Interpreted need and budget
     - Recommended specs
     - Top matching devices

**Run**

```bash
python specs_to_need_bot.py
```

Then type queries like:

```text
I need 3 laptops for video editing under $1600, prefer Windows.
```

The console will show:

- Interpreted need  
- Quantity requested  
- Recommended minimum specs  
- Top matching devices from the sample inventory, including:  
  - price **per device**  
  - **estimated total** for the requested quantity  

**Example queries you can try**

- `I need 3 laptops for video editing under 1600, prefer Windows.`  
- `Need a laptop for photo editing and Photoshop under 1500.`  
- `Looking for a laptop for a school student, budget 900.`  
- `We want a gaming laptop under 2000.`  
- `We need 5 computers for accounting and finance work, budget 800 each.`  
- `Looking for a MacBook for data science and ML, around 2000.`  

---

### 5. How This Supports the Circular Marketplace Concept

- **FMV Engine** – enables consistent, data‑driven pricing of retired corporate devices, helping corporates and refurbishers recover fair value.  
- **Specs‑to‑Need Assistant** – lowers the technical literacy barrier for SMEs by translating business tasks into appropriate hardware specs and recommendations.  

Together, these components illustrate how **analytics** and **AI** can increase pricing transparency, improve “fit‑for‑purpose” purchasing, and support the circular economy for enterprise hardware.

