from __future__ import annotations

from flask import Flask, render_template, request

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

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            # If the text clearly doesn't mention any device type or numbers,
            # treat it as an invalid/ambiguous query instead of returning random results.
            lowered = query.lower()
            device_keywords = [
                "laptop",
                "pc",
                "computer",
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
                    "Please mention at least one device type (laptop, phone, "
                    "iPad, keyboard) or a budget/quantity so the assistant "
                    "has something to optimise for."
                )
            else:
                req, laptops_df, _, keyboards_df, phones_df, ipads_df = recommend_devices(
                    query
                )

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

    return render_template(
        "index.html",
        query=query,
        summary=summary,
        laptops=laptops,
        keyboards=keyboards,
        phones=phones,
        ipads=ipads,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

