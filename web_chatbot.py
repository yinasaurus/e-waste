from __future__ import annotations

from flask import Flask, jsonify, render_template, request
import pandas as pd

from specs_to_need_bot import recommend_devices, estimate_used_price


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    query = ""

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

    if request.method == "POST":
        query = request.form.get("query", "").strip()
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

    return render_template(
        "index.html",
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
    )


def _format_chat_reply(
    req: dict,
    laptops_df: pd.DataFrame,
    desktop_recs: dict,
    keyboards_df: pd.DataFrame,
    phones_df: pd.DataFrame,
    ipads_df: pd.DataFrame,
) -> str:
    """Create a compact plain-text reply for the floating chat widget."""
    lines: list[str] = []

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
    job_label = job_map.get(req.get("job_function"), "General Use")
    budget = req.get("budget")
    qty = req.get("quantity", 1)
    lines.append(
        f"Detected need: {job_label} | Qty: {qty} | Budget: SGD {budget if budget else 'Not specified'}"
    )

    if not laptops_df.empty:
        lines.append("")
        lines.append("Top laptop picks:")
        for _, row in laptops_df.head(3).iterrows():
            new_price = float(row["price_sgd"])
            used_price = estimate_used_price(new_price)
            lines.append(
                f"- {row['brand']} {row['model']} (new ~ SGD {new_price:.0f}, used ~ SGD {used_price:.0f})"
            )

    desktop_cpu = desktop_recs.get("cpu", pd.DataFrame())
    if not desktop_cpu.empty:
        lines.append("")
        lines.append("Desktop parts suggestion:")
        best_cpu = desktop_cpu.iloc[0]
        cpu_new = float(best_cpu["price_sgd"])
        cpu_used = estimate_used_price(cpu_new)
        lines.append(
            f"- CPU: {best_cpu['brand']} {best_cpu['item_desc']} (new ~ SGD {cpu_new:.0f}, used ~ SGD {cpu_used:.0f})"
        )

    if not keyboards_df.empty:
        k = keyboards_df.iloc[0]
        new_price = float(k["price_sgd"])
        used_price = estimate_used_price(new_price)
        lines.append("")
        lines.append(
            f"Keyboard: {k['name']} (new ~ SGD {new_price:.0f}, used ~ SGD {used_price:.0f})"
        )

    if not phones_df.empty:
        p = phones_df.iloc[0]
        new_price = float(p["price_sgd"])
        used_price = estimate_used_price(new_price)
        lines.append("")
        lines.append(
            f"Phone: {p['brand']} {p['model']} (new ~ SGD {new_price:.0f}, used ~ SGD {used_price:.0f})"
        )

    if not ipads_df.empty:
        i = ipads_df.iloc[0]
        new_price = float(i["price_sgd"])
        used_price = estimate_used_price(new_price)
        lines.append("")
        lines.append(
            f"Tablet: {i['product_name']} {i['storage']} (new ~ SGD {new_price:.0f}, used ~ SGD {used_price:.0f})"
        )

    if len(lines) == 1:
        lines.append("")
        lines.append(
            "I could not find a strong match. Try adding device type, budget, and quantity."
        )

    return "\n".join(lines)


def _to_chat_rows(rows: list[dict], keys: list[str]) -> list[dict]:
    """Limit and filter row keys for chat widget tables."""
    trimmed: list[dict] = []
    for row in rows[:3]:
        trimmed.append({k: row.get(k) for k in keys})
    return trimmed


@app.route("/chipcycle", methods=["GET"])
def chipcycle_page():
    return render_template("chipcycle.html")


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    query = str(payload.get("message", "")).strip()

    if not query:
        return jsonify({"reply": "Please type a message first."}), 400

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
        return jsonify(
            {
                "reply": (
                    "Please mention a device type (laptop, desktop, phone, iPad, keyboard) "
                    "or include a budget/quantity so I can recommend properly."
                )
            }
        )

    (
        req,
        laptops_df,
        desktop_recs,
        _mouse_df,
        keyboards_df,
        phones_df,
        ipads_df,
    ) = recommend_devices(query)
    reply = _format_chat_reply(
        req=req,
        laptops_df=laptops_df,
        desktop_recs=desktop_recs,
        keyboards_df=keyboards_df,
        phones_df=phones_df,
        ipads_df=ipads_df,
    )

    laptops_rows = []
    for _, row in laptops_df.iterrows():
        new_price = float(row["price_sgd"])
        laptops_rows.append(
            {
                "brand": str(row["brand"]),
                "model": str(row["model"]),
                "new": int(round(new_price, 0)),
                "used": int(round(estimate_used_price(new_price), 0)),
            }
        )

    keyboards_rows = []
    for _, row in keyboards_df.iterrows():
        new_price = float(row["price_sgd"])
        keyboards_rows.append(
            {
                "name": str(row["name"]),
                "connection": str(row.get("connection", "Unknown")),
                "new": int(round(new_price, 0)),
                "used": int(round(estimate_used_price(new_price), 0)),
            }
        )

    phones_rows = []
    for _, row in phones_df.iterrows():
        new_price = float(row["price_sgd"])
        phones_rows.append(
            {
                "brand": str(row["brand"]),
                "model": str(row["model"]),
                "ram_gb": int(row["ram_gb"]) if not pd.isna(row["ram_gb"]) else 0,
                "storage_gb": (
                    int(row["storage_gb"]) if not pd.isna(row["storage_gb"]) else 0
                ),
                "new": int(round(new_price, 0)),
                "used": int(round(estimate_used_price(new_price), 0)),
            }
        )

    ipads_rows = []
    for _, row in ipads_df.iterrows():
        new_price = float(row["price_sgd"])
        ipads_rows.append(
            {
                "model": str(row["product_name"]),
                "storage": str(row["storage"]),
                "new": int(round(new_price, 0)),
                "used": int(round(estimate_used_price(new_price), 0)),
            }
        )

    desktop_cpu_rows = []
    for _, row in desktop_recs.get("cpu", pd.DataFrame()).iterrows():
        new_price = float(row["price_sgd"])
        desktop_cpu_rows.append(
            {
                "brand": str(row["brand"]),
                "item": str(row["item_desc"]),
                "new": int(round(new_price, 0)),
                "used": int(round(estimate_used_price(new_price), 0)),
            }
        )

    payload = {
        "summary": {
            "job_function": req.get("job_function", "general_office"),
            "quantity": req.get("quantity", 1),
            "budget": req.get("budget"),
        },
        "laptops": _to_chat_rows(laptops_rows, ["brand", "model", "new", "used"]),
        "desktop_cpu": _to_chat_rows(
            desktop_cpu_rows, ["brand", "item", "new", "used"]
        ),
        "keyboards": _to_chat_rows(
            keyboards_rows, ["name", "connection", "new", "used"]
        ),
        "phones": _to_chat_rows(
            phones_rows, ["brand", "model", "ram_gb", "storage_gb", "new", "used"]
        ),
        "ipads": _to_chat_rows(ipads_rows, ["model", "storage", "new", "used"]),
    }
    return jsonify({"reply": reply, "results": payload})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

