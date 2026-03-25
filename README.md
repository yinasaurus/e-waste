## Circular Economy for E‑Waste – Analytics & AI Prototype

This repository contains a **Python prototype** for a B2B circular marketplace that extends the life of corporate IT hardware and helps SMEs buy affordable, fit‑for‑purpose devices.

It demonstrates two core components:

1. **FMV (Fair Market Value) Pricing Engine** – an analytics module that learns a pricing signal from laptop specs and estimates a fair resale price (FMV) in SGD, then applies a second‑hand discount heuristic.  
2. **Specs‑to‑Need Assistant** – an assistant that turns natural‑language needs into second‑hand‑style recommendations for laptops, desktop parts, keyboards, phones and iPads, using both new‑ish and suggested used prices.

---

### 1. Project Structure

- `data/` – folder containing all CSV datasets (keeps the repo root tidy).  
  - `data/laptop_price.csv` – real‑world laptop specifications and prices (new‑device pricing in euros), used as the core dataset. In this prototype, prices are converted to **approximate SGD** using a fixed FX rate.
  - `data/all_keyboards.csv` – keyboard products with prices and ratings, converted to **approximate SGD** in the bot.
  - `data/Mobile phone price.csv` – smartphone brand + model + specs (RAM, storage, screen size, cameras, battery, price in USD‑like units), converted to **approximate SGD** in the bot.
  - `data/apple_global_sales_dataset.csv` – global Apple sales records; only the **iPad** rows are used to suggest iPads / tablets, with prices converted from USD to **approximate SGD**.
- `data/newegg.csv` – desktop component parts catalog (CPU / RAM / storage / GPU, plus some extras), used to suggest “desktop build” parts with approximate SGD prices.
- `fmv_engine.py` – **analytics side**: ML model that learns a pricing signal from `data/laptop_price.csv` and predicts a fair market value for a laptop in **SGD (approx.)**, based on its specs.
- `specs_to_need_bot.py` – **assistant side**: simple NLP + rules to recommend laptops (or desktop parts) plus accessories (keyboards, phones, iPads) using **SGD (approx.)** prices, based on a natural‑language description of needs.
- `web_chatbot.py` – optional Flask app that exposes the Specs‑to‑Need Assistant in a browser (HTML tables with per‑device new / used prices). The core prototype still works entirely from the console.
- `requirements.txt` – Python dependencies.

(Figma wireframes for the UI are kept separately in Figma and are referenced in the course presentation.)

---

### 2. Setup & Installation

**Prerequisites**

- Python 3.9+ installed (Python 3.11+ also works – you’re using this now).  
- `pip` available on your system.  
- Recommended to use a virtual environment (`python -m venv .venv` then activate it) so packages stay isolated to this project.

**Steps**

```bash
# 1. Clone this repository (or open the folder in Cursor)
git clone https://github.com/yinasaurus/e-waste.git
cd e-waste

# 2. (Optional but recommended) create and activate a virtual env
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On CMD:
.venv\Scripts\activate.bat

# 3. Install dependencies
pip install -r requirements.txt

# 4. Activate Chatbot
python web_chatbot.py

# 5. Open another terminal
cd frontend

# 6. Run web UI
npm run dev
```

If you don’t want to use `requirements.txt`, the **minimum libraries** needed for the console apps are:

```bash
pip install pandas scikit-learn colorama
```

**Quick start**

```bash
# Analytics side – FMV engine (console)
python fmv_engine.py

# Assistant side – console
python specs_to_need_bot.py

# Assistant sid3 - web UI
python web_chatbot.py
```

---

### 3. FMV Pricing Engine (`fmv_engine.py`)

**Goal**

Provide a *data‑driven* fair price estimate for an enterprise laptop, based on:

- Brand, model, CPU  
- RAM, storage size & type  
- GPU type  

**Dataset & features**

The engine now trains on the external CSV `data/laptop_price.csv` (new‑device prices in euros). From that file, the script engineers the following features and converts prices to SGD using a fixed rate (currently `1 EUR ≈ 1.45 SGD`, configurable in the code):

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
4. The function `predict_fmv(device_dict)` takes a Python `dict` describing one device and returns a predicted price (FMV, in SGD).  
5. A small helper `estimate_used_price(new_price, age_years, condition, rarity)` applies a **second‑hand heuristic**:  
   - Starts at **≈ 66% of the FMV** (2/3 rule mentioned in second‑hand forums).  
   - Optionally reduces value for older devices (e.g. >3, >5, >8 years).  
   - Adjusts for condition (e.g. A/mint vs B/fair vs poor/parts) and can slightly increase value for rare/discontinued items.  
6. In `__main__`, the script predicts FMV for a sample device and prints both:  
   - **Predicted Fair Market Value (new‑ish, SGD)**.  
   - **Suggested 2nd‑hand asking price (SGD)** computed via the heuristic above.

**Run**

```bash
python fmv_engine.py
```

You’ll see a demo R² score plus a predicted FMV price printed to the console.

---

### 4. Specs‑to‑Need Assistant (`specs_to_need_bot.py` & `web_chatbot.py`)

**Goal**

Act as a simple “virtual CTO” for non‑technical SME owners:

- User describes needs in plain English (e.g. “gaming laptop under 2500 with keyboard, phone and iPad”).  
- The assistant infers the job type, budget, quantity, and which **device types** are requested.  
- It recommends suitable **laptops or desktop parts** plus optional accessories (keyboards, phones, iPads/tablets) from the CSV inventories.

**Inventories (from CSVs)**

- **Laptops** – from `data/laptop_price.csv` (same features as the FMV engine, with prices converted from EUR to SGD).
- **Keyboards** – from `data/all_keyboards.csv` (price parsed and converted from EUR‑like units to approximate SGD, with ratings and votes).
- **Phones** – from `data/Mobile phone price.csv` (brand + model, RAM, storage, screen size, cameras, battery; prices converted from USD‑like units to approximate SGD).
- **iPads / tablets** – from `data/apple_global_sales_dataset.csv`, filtered to `category == "iPad"`; `discounted_price_usd` converted to approximate SGD.

**How it works**

1. **NLP parsing (`parse_requirements`)**
   - Uses regex and keyword checks to extract:
     - `budget` (first number in the text, treated as SGD per laptop/phone/tablet where prices exist)
     - `quantity` (e.g. “3 laptops”, “for 2”)
     - `os_pref` (`mac`, `windows`, or `any`)
     - `job_function` (high‑level “need” such as video editing, creative design, accounting, data science, software dev, student use, gaming, or general office), inferred from keywords.
     - Flags for which extras are requested: keyboard, phone, tablet/iPad.
   - Includes a small **typo normaliser** for common misspellings (e.g. `ipone` → `iphone`, `labtop` → `laptop`, `andriod` → `android`).
   - Avoids mis‑treating model numbers as budgets (e.g. “iphone 12” will not set budget to \$12).
2. **Specs mapping for laptops (`job_to_min_specs`)**
   - Each `job_function` is mapped to a simple **minimum spec recipe**:
     - Video editing / creative design / gaming → **16GB RAM**, **512GB SSD**, **dedicated GPU**
     - Data science / software development → **16GB RAM**, **512GB SSD**, **integrated GPU OK**
     - Accounting / student use / general office → **8GB RAM**, **256GB SSD**, **integrated GPU OK**
3. **Recommendations (`recommend_devices`)**
   - **Laptops** – filtered by min RAM/storage, GPU requirement, OS preference, and budget in SGD, then:
     - Sorted by **cheapest first**, unless the user says “expensive / premium / high end”, in which case **most expensive** laptops are shown first.  
     - For each laptop, a **suggested 2nd‑hand asking price** is computed using the same `estimate_used_price` heuristic (2/3‑of‑new plus small adjustments for age/condition/rarity when available).  
   - **Keyboards** – filtered (when requested) by connection preference (wireless / Bluetooth / USB), then:
     - Sorted by **highest rating + most votes**, or by **highest price** if the user asks for expensive / premium options.  
     - Each keyboard line also shows a **suggested 2nd‑hand price** based on the same 2/3 rule.  
   - **Phones** – built from `data/Mobile phone price.csv`, filtered by:
     - Budget in SGD (if provided)  
     - Brand hints (e.g. `iphone` / `apple`, `samsung`, `oneplus`)  
     - Simple model matching for iPhones like `"iphone 12 mini"` when specified  
     - Then sorted by specs/price, or by **highest price** if the user says “expensive / premium”.  
     - A **suggested 2nd‑hand price** is shown next to each new‑ish price.  
   - **iPads / tablets** – filtered (when requested) by:
     - Budget in SGD (if provided)  
     - Education / student hints (filters to education segment when “education / student / school” is mentioned)  
     - Then sorted by **rating + price**, or **highest price** when the user asks for expensive / premium tablets.  
     - A **suggested 2nd‑hand price** is shown for each iPad/tablet line.  
4. **Formatting**
   - `specs_to_need_bot.py` produces a colorful, sectioned **console reply** (for quick demos) with:
     - Quantity and budget  
     - Top matching laptops / keyboards / phones / iPads with new vs used prices  
   - `web_chatbot.py` uses the same underlying logic but renders the results in **HTML tables** with per‑device new / used prices for each category.

**Run**

```bash
python specs_to_need_bot.py
```

Then type queries like:

```text
I need 2 gaming laptops under 2500 each, plus a keyboard and phone.
```

or:

```text
Looking for an iPad or tablet around 1200 with a wireless keyboard.
```

---

### 5. Simple Web UI (`web_chatbot.py`)

If you prefer a browser‑based UI instead of the console, you can run a minimal Flask app that wraps the Specs‑to‑Need Assistant.

**Run**

```bash
python web_chatbot.py
```

Then open `http://127.0.0.1:8000` in your browser.  
You’ll see:

- A **single text box** where you can type the same prompts as in the console.  
- A **“Get recommendations”** button.  
- Results rendered in **`templates/index.html`** as HTML tables (without ANSI colour codes), showing:
  - Quantity and budget  
  - Recommended laptops, desktop parts, keyboards, phones and iPads (with new vs suggested 2nd‑hand prices)

**Visual theme:** The page uses the team palette (**#212121**, **#4A4A4A**, **#9D4EDD**, **#FF9100**, **#F7F7F7**) with **Inter** (body) and **Poppins** (headings / primary button), loaded from Google Fonts, so the bot matches the circular‑marketplace branding.

The web app uses the existing `recommend_devices` logic, so recommendations stay consistent between console and browser.

---

### 6. How This Supports the Circular Marketplace Concept

- **FMV Engine** – enables consistent, data‑driven pricing of retired corporate devices, helping corporates and refurbishers recover fair value.  
- **Specs‑to‑Need Assistant** – lowers the technical literacy barrier for SMEs by translating business tasks into appropriate hardware specs and recommendations.  

Together, these components illustrate how **analytics** and **AI** can increase pricing transparency, improve “fit‑for‑purpose” purchasing, and support the circular economy for enterprise hardware:

- The **analytics side** (`fmv_engine.py`) learns a pricing signal from real‑world laptop data and converts it into both an FMV and a realistic second‑hand asking price (≈ 2/3 of new, adjusted for age/condition/rarity).  
- The **assistant side** (`specs_to_need_bot.py` + `web_chatbot.py`) lets non‑technical users describe their needs in plain English and receive concrete second‑hand‑style recommendations (laptops, keyboards, phones, iPads) with clear new vs used price guidance, plus simple validation for illogical prompts.

