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
    }

    laptops: list[dict] = []
    keyboards: list[dict] = []
    phones: list[dict] = []
    ipads: list[dict] = []

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
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
                laptops.append(
                    {
                        "brand": str(row["brand"]),
                        "model": str(row["model"]),
                        "new": round(new_price, 0),
                        "used": estimate_used_price(new_price),
                        "total_new": round(new_price * req["quantity"], 0),
                    }
                )

            # Keyboards
            for _, row in keyboards_df.iterrows():
                new_price = float(row["price_sgd"])
                keyboards.append(
                    {
                        "name": str(row["name"]),
                        "connection": (
                            str(row["connection"])
                            if isinstance(row["connection"], str)
                            else "Unknown"
                        ),
                        "new": round(new_price, 0),
                        "used": estimate_used_price(new_price),
                        "total_new": round(new_price * req["quantity"], 0),
                    }
                )

            # Phones
            for _, row in phones_df.iterrows():
                new_price = float(row["price_sgd"])
                phones.append(
                    {
                        "brand": str(row["brand"]),
                        "model": str(row["model"]),
                        "ram_gb": int(row["ram_gb"]),
                        "storage_gb": int(row["storage_gb"]),
                        "new": round(new_price, 0),
                        "used": estimate_used_price(new_price),
                        "total_new": round(new_price * req["quantity"], 0),
                    }
                )

            # iPads
            for _, row in ipads_df.iterrows():
                new_price = float(row["price_sgd"])
                ipads.append(
                    {
                        "model": str(row["product_name"]),
                        "storage": str(row["storage"]),
                        "new": round(new_price, 0),
                        "used": estimate_used_price(new_price),
                        "total_new": round(new_price * req["quantity"], 0),
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

