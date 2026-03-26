from __future__ import annotations

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd

from fmv_engine import predict_fmv as analytics_predict_fmv
from fmv_engine import estimate_used_price as analytics_estimate_used_price
from specs_to_need_bot import recommend_devices, estimate_used_price


app = Flask(__name__)
CORS(app)     # Allow cross-origin requests from the React frontend

_CHAT_DEVICE_KEYWORDS = (
    "laptop",
    "desktop",
    "pc",
    "computer",
    "tower",
    "ipad",
    "tablet",
    "phone",
    "iphone",
    "android",
    "keyboard",
    "macbook",
    "notebook",
    "chromebook",
    "workstation",
    "all-in-one",
    "aio",
    "imac",
    "surface",
    "pixel",
    "galaxy",
    "oneplus",
)


def _chat_info_message(lowered: str) -> str | None:
    """FAQ / meta queries: return a help string, or None to run normal recommendation."""
    triggers = (
        "what is specs",
        "specs-to-need",
        "specs to need",
        "what is chip",
        "who are you",
        "what can you do",
        "help me",
        "how do you work",
        "how does this work",
        "what do you do",
    )
    if any(t in lowered for t in triggers):
        return (
            "I'm Chip, your Specs-to-Need assistant. I turn a short description of what you need "
            "into concrete picks from our demo catalog — laptops, desktop parts, keyboards, phones, "
            "or iPads — with approximate new and used SGD prices (used ≈ 66% of new, plus simple rules).\n\n"
            "This is separate from the FMV page: FMV is a structured laptop pricing model; I help you "
            "browse categories from natural language.\n\n"
            "Try examples:\n"
            "• Gaming laptop under 2000\n"
            "• Office desktop PC budget 3500\n"
            "• Wireless keyboard under 80\n"
            "• Student iPad under 1200\n\n"
            "Include a device type or a budget/number so results stay relevant.\n\n"
            "Note: Chip uses keyword and catalog rules (not a live web LLM), so edge phrasing "
            "can still mis-fire — rephrase with explicit device + budget if a reply looks off."
        )
    return None


def _query_has_device_or_budget_hint(lowered: str) -> bool:
    return any(k in lowered for k in _CHAT_DEVICE_KEYWORDS) or any(
        ch.isdigit() for ch in lowered
    )


def _fmv_from_device_payload(payload: dict) -> tuple[dict | None, str | None]:
    """
    Build FMV + used estimate from JSON/form-like dict.
    Returns (result_dict, error_message). result has keys fmv_sgd, used_sgd, device.
    """
    brand = str(payload.get("brand") or payload.get("fmv_brand") or "").strip()
    model = str(payload.get("model") or payload.get("fmv_model") or "").strip()
    cpu = str(payload.get("cpu") or payload.get("fmv_cpu") or "").strip()
    if not brand or not model or not cpu:
        return None, "Brand, model, and CPU are required for FMV."

    try:
        ram_gb = int(payload.get("ram_gb") if payload.get("ram_gb") is not None else payload.get("fmv_ram_gb") or 8)
    except (TypeError, ValueError):
        return None, "RAM (GB) must be a whole number."

    try:
        storage_gb = int(
            payload.get("storage_gb")
            if payload.get("storage_gb") is not None
            else payload.get("fmv_storage_gb")
            or 256
        )
    except (TypeError, ValueError):
        return None, "Storage (GB) must be a whole number."

    storage_type = str(
        payload.get("storage_type") or payload.get("fmv_storage_type") or "SSD"
    ).strip()
    if storage_type.upper() not in {"SSD", "HDD"}:
        storage_type = "SSD"

    gpu_type = str(
        payload.get("gpu_type") or payload.get("fmv_gpu_type") or "integrated"
    ).strip().lower()
    if gpu_type not in {"integrated", "dedicated"}:
        gpu_type = "integrated"

    device = {
        "brand": brand,
        "model": model,
        "cpu": cpu,
        "ram_gb": ram_gb,
        "storage_gb": storage_gb,
        "storage_type": storage_type,
        "gpu_type": gpu_type,
    }

    age_raw = payload.get("age_years") if payload.get("age_years") is not None else payload.get("fmv_age_years")
    age_years: float | None = None
    if age_raw not in (None, ""):
        try:
            age_years = float(age_raw)
        except (TypeError, ValueError):
            return None, "Age (years) must be a number."

    condition = payload.get("condition") or payload.get("fmv_condition")
    condition = str(condition).strip() if condition else None

    fmv_price = analytics_predict_fmv(device)
    used_price = analytics_estimate_used_price(
        new_price=fmv_price,
        age_years=age_years,
        condition=condition,
    )

    return (
        {
            "fmv_sgd": round(float(fmv_price), 2),
            "used_sgd": float(used_price),
            "device": device,
            "age_years": age_years,
            "condition": condition,
        },
        None,
    )


@app.route("/api/fmv", methods=["POST"])
def api_fmv():
    data = request.get_json() or {}
    result, err = _fmv_from_device_payload(data)
    if err:
        return jsonify(error=err), 400
    return jsonify(result), 200


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    summary = {
        "job_label": None,
        "quantity": None,
        "budget": None,
        "error": None,
        "info": None,
        "hint": None,
    }

    laptops: list[dict] = []
    keyboards: list[dict] = []
    phones: list[dict] = []
    ipads: list[dict] = []
    desktop_cpu: list[dict] = []
    desktop_ram: list[dict] = []
    desktop_storage: list[dict] = []
    desktop_gpu: list[dict] = []

    if query:
        lowered = query.lower()
        info_msg = _chat_info_message(lowered)
        if info_msg:
            summary["info"] = info_msg
        elif not _query_has_device_or_budget_hint(lowered):
            summary["error"] = (
                "Please mention at least one device type (laptop, desktop, "
                "phone, iPad, keyboard, MacBook, etc.) or a budget/quantity so "
                "the assistant has something to optimise for."
            )
        else:
            (
                req,
                laptops_df,
                desktop_recs,
                _mouse_df,
                keyboards_df,
                phones_df,
                ipads_df,
            ) = recommend_devices(query)

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
            summary["job_label"] = job_map.get(req["job_function"], "General Use")
            summary["quantity"] = req["quantity"]
            summary["budget"] = req["budget"]
            summary["hint"] = req.get("assistant_note")

            # Laptops
            for _, row in laptops_df.iterrows():
                new_price = float(row["price_sgd"])
                used_price = estimate_used_price(new_price)
                laptops.append(
                    {
                        "brand": str(row["brand"]),
                        "model": str(row["model"]),
                        "new": round(new_price, 0),
                        "used": used_price,
                    }
                )

            # Keyboards
            for _, row in keyboards_df.iterrows():
                new_price = float(row["price_sgd"])
                used_price = estimate_used_price(new_price)
                keyboards.append(
                    {
                        "name": str(row["name"]),
                        "connection": (
                            str(row["connection"])
                            if isinstance(row["connection"], str)
                            else "Unknown"
                        ),
                        "new": round(new_price, 0),
                        "used": used_price,
                    }
                )

            # Phones
            for _, row in phones_df.iterrows():
                new_price = float(row["price_sgd"])
                used_price = estimate_used_price(new_price)
                phones.append(
                    {
                        "brand": str(row["brand"]),
                        "model": str(row["model"]),
                        "ram_gb": int(row["ram_gb"]),
                        "storage_gb": int(row["storage_gb"]),
                        "new": round(new_price, 0),
                        "used": used_price,
                    }
                )

            # iPads
            for _, row in ipads_df.iterrows():
                new_price = float(row["price_sgd"])
                used_price = estimate_used_price(new_price)
                ipads.append(
                    {
                        "model": str(row["product_name"]),
                        "storage": str(row["storage"]),
                        "new": round(new_price, 0),
                        "used": used_price,
                    }
                )

            # Desktop parts (CPU / RAM / Storage / optional GPU)
            for _, row in desktop_recs.get("cpu", pd.DataFrame()).iterrows():
                new_price = float(row["price_sgd"])
                used_price = estimate_used_price(new_price)
                desktop_cpu.append(
                    {
                        "brand": str(row["brand"]),
                        "item": str(row["item_desc"]),
                        "new": round(new_price, 0),
                        "used": used_price,
                    }
                )

            for _, row in desktop_recs.get("ram", pd.DataFrame()).iterrows():
                new_price = float(row["price_sgd"])
                used_price = estimate_used_price(new_price)
                desktop_ram.append(
                    {
                        "ram_gb": int(row["ram_gb"]) if not pd.isna(row["ram_gb"]) else 0,
                        "new": round(new_price, 0),
                        "used": used_price,
                    }
                )

            for _, row in desktop_recs.get("storage", pd.DataFrame()).iterrows():
                new_price = float(row["price_sgd"])
                used_price = estimate_used_price(new_price)
                desktop_storage.append(
                    {
                        "storage_gb": int(row["storage_gb"])
                        if not pd.isna(row["storage_gb"])
                        else 0,
                        "storage_type": str(row.get("storage_type", "unknown")),
                        "new": round(new_price, 0),
                        "used": used_price,
                    }
                )

            for _, row in desktop_recs.get("gpu", pd.DataFrame()).iterrows():
                new_price = float(row["price_sgd"])
                used_price = estimate_used_price(new_price)
                desktop_gpu.append(
                    {
                        "brand": str(row["brand"]),
                        "item": str(row["item_desc"]),
                        "new": round(new_price, 0),
                        "used": used_price,
                    }
                )

    return jsonify(
        query=query,
        summary=summary,
        laptops=laptops,
        keyboards=keyboards,
        phones=phones,
        ipads=ipads,
        desktop_cpu=desktop_cpu,
        desktop_ram=desktop_ram,
        desktop_storage=desktop_storage,
        desktop_gpu=desktop_gpu,
    ), 200

# Keep the original route for backward compatibility locally if needed
@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    fmv_result: dict | None = None
    fmv_form = {
        "brand": "",
        "model": "",
        "cpu": "",
        "ram_gb": "16",
        "storage_gb": "512",
        "storage_type": "SSD",
        "gpu_type": "integrated",
        "age_years": "",
        "condition": "",
    }
    summary = {
        "job_label": None,
        "quantity": None,
        "budget": None,
        "error": None,
        "info": None,
        "hint": None,
    }

    laptops: list[dict] = []
    keyboards: list[dict] = []
    phones: list[dict] = []
    ipads: list[dict] = []
    desktop_cpu: list[dict] = []
    desktop_ram: list[dict] = []
    desktop_storage: list[dict] = []
    desktop_gpu: list[dict] = []

    if request.method == "POST":
        if request.form.get("form_type") == "fmv":
            fmv_form = {
                "brand": request.form.get("fmv_brand", "").strip(),
                "model": request.form.get("fmv_model", "").strip(),
                "cpu": request.form.get("fmv_cpu", "").strip(),
                "ram_gb": request.form.get("fmv_ram_gb", "16").strip() or "16",
                "storage_gb": request.form.get("fmv_storage_gb", "512").strip() or "512",
                "storage_type": request.form.get("fmv_storage_type", "SSD").strip() or "SSD",
                "gpu_type": request.form.get("fmv_gpu_type", "integrated").strip()
                or "integrated",
                "age_years": request.form.get("fmv_age_years", "").strip(),
                "condition": request.form.get("fmv_condition", "").strip(),
            }
            result, err = _fmv_from_device_payload(
                {
                    "fmv_brand": fmv_form["brand"],
                    "fmv_model": fmv_form["model"],
                    "fmv_cpu": fmv_form["cpu"],
                    "fmv_ram_gb": fmv_form["ram_gb"],
                    "fmv_storage_gb": fmv_form["storage_gb"],
                    "fmv_storage_type": fmv_form["storage_type"],
                    "fmv_gpu_type": fmv_form["gpu_type"],
                    "fmv_age_years": fmv_form["age_years"] or None,
                    "fmv_condition": fmv_form["condition"] or None,
                }
            )
            if err:
                fmv_result = {"error": err}
            else:
                fmv_result = result
        else:
            query = request.form.get("query", "").strip()
            if query:
                lowered = query.lower()
                info_msg = _chat_info_message(lowered)
                if info_msg:
                    summary["info"] = info_msg
                elif not _query_has_device_or_budget_hint(lowered):
                    summary["error"] = (
                        "Please mention at least one device type (laptop, desktop, "
                        "phone, iPad, keyboard, MacBook, etc.) or a budget/quantity so "
                        "the assistant has something to optimise for."
                    )
                else:
                    (
                        req,
                        laptops_df,
                        desktop_recs,
                        _mouse_df,
                        keyboards_df,
                        phones_df,
                        ipads_df,
                    ) = recommend_devices(query)
    
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
                    summary["job_label"] = job_map.get(req["job_function"], "General Use")
                    summary["quantity"] = req["quantity"]
                    summary["budget"] = req["budget"]
                    summary["hint"] = req.get("assistant_note")
    
                    for _, row in laptops_df.iterrows():
                        new_price = float(row["price_sgd"])
                        used_price = estimate_used_price(new_price)
                        laptops.append(
                            {
                                "brand": str(row["brand"]),
                                "model": str(row["model"]),
                                "new": round(new_price, 0),
                                "used": used_price,
                            }
                        )
    
                    for _, row in keyboards_df.iterrows():
                        new_price = float(row["price_sgd"])
                        used_price = estimate_used_price(new_price)
                        keyboards.append(
                            {
                                "name": str(row["name"]),
                                "connection": (
                                    str(row["connection"])
                                    if isinstance(row["connection"], str)
                                    else "Unknown"
                                ),
                                "new": round(new_price, 0),
                                "used": used_price,
                            }
                        )
    
                    for _, row in phones_df.iterrows():
                        new_price = float(row["price_sgd"])
                        used_price = estimate_used_price(new_price)
                        phones.append(
                            {
                                "brand": str(row["brand"]),
                                "model": str(row["model"]),
                                "ram_gb": int(row["ram_gb"]),
                                "storage_gb": int(row["storage_gb"]),
                                "new": round(new_price, 0),
                                "used": used_price,
                            }
                        )
    
                    for _, row in ipads_df.iterrows():
                        new_price = float(row["price_sgd"])
                        used_price = estimate_used_price(new_price)
                        ipads.append(
                            {
                                "model": str(row["product_name"]),
                                "storage": str(row["storage"]),
                                "new": round(new_price, 0),
                                "used": used_price,
                            }
                        )
    
                    # Desktop parts (CPU / RAM / Storage / optional GPU)
                    for _, row in desktop_recs.get("cpu", pd.DataFrame()).iterrows():
                        new_price = float(row["price_sgd"])
                        used_price = estimate_used_price(new_price)
                        desktop_cpu.append(
                            {
                                "brand": str(row["brand"]),
                                "item": str(row["item_desc"]),
                                "new": round(new_price, 0),
                                "used": used_price,
                            }
                        )
    
                    for _, row in desktop_recs.get("ram", pd.DataFrame()).iterrows():
                        new_price = float(row["price_sgd"])
                        used_price = estimate_used_price(new_price)
                        desktop_ram.append(
                            {
                                "ram_gb": int(row["ram_gb"]) if not pd.isna(row["ram_gb"]) else 0,
                                "new": round(new_price, 0),
                                "used": used_price,
                            }
                        )
    
                    for _, row in desktop_recs.get("storage", pd.DataFrame()).iterrows():
                        new_price = float(row["price_sgd"])
                        used_price = estimate_used_price(new_price)
                        desktop_storage.append(
                            {
                                "storage_gb": int(row["storage_gb"])
                                if not pd.isna(row["storage_gb"])
                                else 0,
                                "storage_type": str(
                                    row.get("storage_type", "unknown")
                                ),
                                "new": round(new_price, 0),
                                "used": used_price,
                            }
                        )
    
                    for _, row in desktop_recs.get("gpu", pd.DataFrame()).iterrows():
                        new_price = float(row["price_sgd"])
                        used_price = estimate_used_price(new_price)
                        desktop_gpu.append(
                            {
                                "brand": str(row["brand"]),
                                "item": str(row["item_desc"]),
                                "new": round(new_price, 0),
                                "used": used_price,
                            }
                        )

    return render_template(
        "index.html",
        query=query,
        summary=summary,
        fmv_result=fmv_result,
        fmv_form=fmv_form,
        laptops=laptops,
        keyboards=keyboards,
        phones=phones,
        ipads=ipads,
        desktop_cpu=desktop_cpu,
        desktop_ram=desktop_ram,
        desktop_storage=desktop_storage,
        desktop_gpu=desktop_gpu,
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

