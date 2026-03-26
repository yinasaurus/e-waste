# Circular economy for e-waste — analytics & AI prototype

Python prototype for a B2B circular marketplace: **FMV pricing** (laptops) and a **Specs-to-Need assistant** (laptops, desktop parts, keyboards, phones, iPads) with approximate **SGD** prices and a simple second-hand heuristic.

---

## Contents

1. [Project layout](#project-layout)
2. [Install & run](#install--run)
3. [FMV engine](#fmv-engine-fmv_enginepy)
4. [Specs-to-Need assistant](#specs-to-need-assistant-specs_to_need_botpy--web_chatbotpy)
5. [Chip chat (React)](#chip-chat-react--ask-chip)
6. [How budget works](#how-budget-works)
7. [Why this fits a circular marketplace](#why-this-fits-a-circular-marketplace)

---

## Project layout

| Path | Role |
|------|------|
| `data/laptop_price.csv` | Laptop specs & EUR list prices → SGD in code |
| `data/all_keyboards.csv` | Keyboards (EUR-like) → SGD |
| `data/Mobile phone price.csv` | Phones (USD-like) → SGD |
| `data/apple_global_sales_dataset.csv` | iPad rows only → SGD |
| `data/newegg.csv` | Desktop parts (CPU / RAM / storage / GPU, etc.) → SGD |
| `fmv_engine.py` | **Analytics:** Random Forest FMV for laptops + `estimate_used_price()` |
| `specs_to_need_bot.py` | **Assistant:** NLP + rules → recommendations (console) |
| `web_chatbot.py` | **Web/API:** Flask — browser UI and/or `POST /api/chat` for the React app |
| `frontend/` | Vite + React shell (`ChipCycle`) + **Ask Chip** chat widget |
| `frontend/src/config.js` | `VITE_API_BASE` → Flask origin (default `http://127.0.0.1:8000`) |
| `requirements.txt` | Python dependencies |

---

## Install & run

**Requirements:** Python 3.9+, Node.js + npm (only if you use `frontend/`).

### Python

```bash
git clone https://github.com/yinasaurus/e-waste.git
cd e-waste

python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Run (pick what you need)

| What | Command | Open / note |
|------|---------|-------------|
| FMV demo (console) | `python fmv_engine.py` | Terminal output |
| Assistant (console) | `python specs_to_need_bot.py` | Interactive prompts |
| Flask app | `python web_chatbot.py` | `http://127.0.0.1:8000/` — **FMV** form + **assistant** on one page; APIs `POST /api/fmv` & `POST /api/chat` |
| React dev server | `cd frontend` then `npm ci` then `npm run dev` | `http://127.0.0.1:5173/` |

If `npm run dev` says `'vite' is not recognized`, install deps first: `cd frontend` → `npm ci`.  
If `npm ci` hits **EPERM** on a `.node` file, stop any running Vite/`npm run dev` (Ctrl+C), then run `npm ci` again.

**Minimal pip-only stack** (if you skip `requirements.txt`):  
`pip install pandas scikit-learn colorama flask flask-cors`

---

## FMV engine (`fmv_engine.py`)

- Trains on `data/laptop_price.csv`: brand, model, CPU, RAM, storage, GPU type; label is **price in SGD** (EUR × fixed rate, e.g. ≈ 1.45).
- **Pipeline:** one-hot categoricals + numeric features → `RandomForestRegressor`.
- **`estimate_used_price(new_price, ...)`:** ≈ **66% of new** (2/3 rule), with optional tweaks for age, condition, rarity.
- Run: `python fmv_engine.py` — prints a sample predicted FMV and suggested second-hand ask.

**On the web:** With `python web_chatbot.py`, open `http://127.0.0.1:8000/` and use the **Laptop FMV (analytics)** card (same `predict_fmv()` as the engine). Optional **age** and **condition** fields feed the analytics `estimate_used_price()` heuristic.  
**API (e.g. React):** `POST /api/fmv` with JSON such as:

```json
{
  "brand": "Dell",
  "model": "XPS 13",
  "cpu": "Intel Core i5 8250U 1.6GHz",
  "ram_gb": 16,
  "storage_gb": 512,
  "storage_type": "SSD",
  "gpu_type": "integrated",
  "age_years": 3,
  "condition": "B"
}
```

Response includes `fmv_sgd`, `used_sgd`, and echo `device` fields. First server start may take a moment while the model loads from `fmv_engine.py`.

---

## Specs-to-Need assistant (`specs_to_need_bot.py` + `web_chatbot.py`)

**Flow**

1. **`parse_requirements`** — regex / keywords: budget, quantity (`for 2`, `need 3`, `3 laptops`), OS hint, **job** (gaming, dev, student, etc.), device flags (laptop, desktop/tower/PC, keyboard, phone, tablet). Typo fixes (e.g. `ipone`→`iphone`). iPhone model numbers are not treated as tiny budgets.
2. **`job_to_min_specs`** — maps job to min RAM / storage and whether a **dedicated GPU** is expected.
3. **`recommend_devices`** — filters inventories, applies budget where relevant, sorts results, attaches **used** prices via `estimate_used_price`.

**Inventories**

- Laptops → `data/laptop_price.csv`
- Desktop **parts** (not full pre-builts) → `data/newegg.csv`
- Keyboards, phones, iPads → respective CSVs under `data/`

**Interfaces**

- **Console:** `python specs_to_need_bot.py`
- **Browser:** `python web_chatbot.py` → form at `http://127.0.0.1:8000/` (HTML in `templates/index.html`).
- **JSON API:** `POST /api/chat` with JSON body `{"query":"..."}` — for the React `frontend/` (CORS enabled). Response shape:
  - `summary.job_label`, `summary.quantity`, `summary.budget` — inferred when recommendations run.
  - `summary.error` — validation (e.g. missing device type and no budget/digit in the text).
  - `summary.info` — static help / FAQ for questions like “What is Specs-to-Need?” (no product rows).
  - `laptops`, `keyboards`, `phones`, `ipads`, `desktop_cpu`, `desktop_ram`, `desktop_storage`, `desktop_gpu` — rows with `new` / `used` (SGD, approximate).

### Chip chat (React) — Ask Chip

- **UI:** `frontend/src/ChatbotWidget.jsx` (styles in `ChatbotWidget.css`). Shown from `App.jsx` on top of `ChipCycle`.
- **Backend:** same Flask app as the HTML form; ensure `python web_chatbot.py` is running before `npm run dev`.
- **Config:** optional `frontend/.env` with `VITE_API_BASE=http://127.0.0.1:8000` if the API is not on the default host/port.
- **FMV vs Chip:** the **FMV Check** page posts structured laptop fields to `POST /api/fmv`. **Ask Chip** uses natural language on `POST /api/chat`. They are separate features.

---

## How budget works

The assistant treats **budget as a maximum** in **SGD (approx.)**, not as “spend exactly this much.”

1. Items are kept only if **price ≤ budget** (where the dataset has a price).
2. By default, results are sorted **cheapest first** among options that still meet the minimum specs.

So a very high budget (e.g. **100000**) means *almost everything qualifies*; you still get the **cheapest** qualifying picks, not automatically the most premium. That is intentional for a “stay under cap” reading of budget.

**To bias toward premium options**, include words like **`expensive`**, **`premium`**, or **`high end`** in your prompt — then the assistant sorts **highest price first** (where that rule applies).

**Desktop parts:** budget is split across CPU / RAM / storage / optional GPU heuristics inside the bot; it is still an upper bound, not a target spend.

---

## Why this fits a circular marketplace

- **FMV engine** — data-driven resale pricing for laptops; transparent “new-ish” vs suggested second-hand ask.
- **Assistant** — turns plain-language needs into concrete hardware suggestions with **new vs used** guidance, so SMEs don’t need to master spec sheets.

Together they illustrate analytics + lightweight “AI” (rules + ML) supporting reuse and fair pricing of enterprise hardware.
