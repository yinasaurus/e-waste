from __future__ import annotations

import os

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd

from specs_to_need_bot import recommend_devices, estimate_used_price


app = Flask(__name__)
CORS(app)     # Allow cross-origin requests from the React frontend


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    summary = {
        "job_label": None,
        "quantity": None,
        "budget": None,
        "error": None,
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
            # If the text clearly doesn't mention any device type or numbers,
            # treat it as an invalid/ambiguous query instead of returning random results.
            lowered = query.lower()
            device_keywords = [
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
            ]
            if not any(k in lowered for k in device_keywords) and not any(
                ch.isdigit() for ch in lowered
            ):
                summary["error"] = (
                    "Please mention at least one device type (laptop, desktop, "
                    "phone, iPad, keyboard) or a budget/quantity so the assistant "
                    "has something to optimise for."
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
                            "storage_gb": int(row["storage_gb"]) if not pd.isna(row["storage_gb"]) else 0,
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
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

