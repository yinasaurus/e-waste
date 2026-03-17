## Circular Economy for E‑Waste – Analytics & AI Prototype

This repository contains the **Python prototype** for a B2B circular marketplace that extends the life of corporate IT hardware and helps SMEs buy affordable, fit‑for‑purpose devices.

It demonstrates two core components of the platform:

1. **FMV (Fair Market Value) Pricing Engine** – estimates a fair resale price for used laptops based on specs and condition.  
2. **Specs‑to‑Need Assistant** – an AI‑style helper that translates business needs (in plain English) into hardware recommendations using a small inventory.

---

### 1. Project Structure

- `laptop_price.csv` – real‑world laptop specifications and prices (new‑device pricing in euros), used as the core dataset. In this prototype, prices are converted to **approximate SGD** using a fixed FX rate.
- `fmv_engine.py` – ML model that learns a pricing signal from `laptop_price.csv` and predicts a fair market value for a laptop in **SGD (approx.)**, based on its specs.
- `specs_to_need_bot.py` – simple NLP + rules to recommend laptops from the `laptop_price.csv` inventory, using **SGD (approx.)** prices in the UI, based on a natural‑language description of needs.
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

Provide a *data‑driven* fair price estimate for an enterprise laptop, based on:

- Brand, model, CPU
- RAM, storage size & type
- GPU type

**Dataset & features**

The engine now trains on the external CSV `laptop_price.csv` (new‑device prices in euros). From that file, the script engineers the following features and converts prices to SGD using a fixed rate (currently `1 EUR ≈ 1.45 SGD`, configurable in the code):

- **`brand`** – from `Company` (laptop manufacturer, e.g. Dell, HP, Lenovo, Apple).  
- **`model`** – from `Product` (specific model name).  
- **`cpu`** – from `Cpu` (full CPU string, e.g. `Intel Core i5 8250U 1.6GHz`).  
- **`ram_gb`** – parsed from `Ram` (e.g. `"8GB"` → `8`).  
- **`storage_gb`** – primary storage capacity in GB, parsed from `Memory` (handles values like `256GB SSD`, `128GB SSD + 1TB HDD`).  
- **`storage_type`** – `"SSD"` or `"HDD"`, inferred from `Memory`.  
- **`gpu_type`** – `"integrated"` vs `"dedicated"`, inferred from `Gpu` (Nvidia/AMD treated as dedicated).  
- **`price_eur`** – the price from `Price_euros`.  
- **`price_sgd`** – price converted from euros to SGD (approx.) used as the **label** (`y`) the model learns to predict.

**How it works**

1. The CSV dataset is loaded into a Pandas DataFrame, feature‑engineered into the columns above, and prices are converted from euros to SGD (approx.).  
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

Act as a simple “virtual CTO” for non‑technical SME owners, focused on **laptops only**:

- User describes needs in plain English (e.g. “laptop for video editing under $1500”).  
- The bot infers the job type, budget, and OS preference.  
- It recommends suitable devices from a small inventory.

**Inventory dataset (from CSV)**

Instead of a tiny hard‑coded list, the assistant builds its inventory directly from `laptop_price.csv`:

- `id` – from `laptop_ID` (internal ID of the listing).  
- `brand` – from `Company`.  
- `model` – from `Product`.  
- `cpu` – from `Cpu`.  
- `ram_gb` – parsed from `Ram`.  
- `storage_gb`, `storage_type` – parsed from `Memory` (SSD / HDD capacity).  
- `gpu_type` – `"integrated"` or `"dedicated"`, inferred from `Gpu`.  
- `price` – from `Price_euros` (used as price per device).

**How it works**

1. **NLP parsing (`parse_requirements`)**
   - Uses regex and keyword checks to extract:
     - `budget` (first number in the text, treated as SGD per device)
     - `quantity` (e.g. “3 laptops”)
     - `os_pref` (`mac`, `windows`, or `any`)
     - `job_function` (high‑level “need” such as video editing, creative design, accounting, data science, software dev, student use, gaming, or general office), inferred from keywords in the sentence.
2. **Specs mapping (`job_to_min_specs`)**
   - Each `job_function` is mapped to a simple **minimum spec recipe**:
     - Video editing / creative design / gaming → **16GB RAM**, **512GB SSD**, **dedicated GPU**
     - Data science / software development → **16GB RAM**, **512GB SSD**, **integrated GPU OK**
     - Accounting / student use / general office → **8GB RAM**, **256GB SSD**, **integrated GPU OK**
3. **Recommendation (`recommend_devices`)**
   - Filters the CSV‑based inventory by:
     - Minimum RAM (`min_ram`) and storage (`min_storage`)
     - GPU requirement (`needs_gpu`)
     - Budget per device in SGD
     - OS preference (Mac vs Windows)
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

