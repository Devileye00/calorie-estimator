import json

from flask import Flask, Response, jsonify, render_template, request

from model import DISHES, EXTRAS, SIZES, load_model, predict_nutrition

app = Flask(__name__)
model = load_model()

DAILY_KCAL = 2000


def meal_label(kcal):
    if kcal < 300:
        return "Light snack"
    if kcal < 600:
        return "Moderate meal"
    return "Heavy meal"


def parse_item(data):
    """Validate one meal item. Returns ((dish, size, extra, qty), error)."""
    dish, size, extra = data.get("dish"), data.get("size"), data.get("extra")
    try:
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return None, "Quantity must be a whole number."
    if dish not in DISHES:
        return None, "Please choose a dish from the list."
    if size not in SIZES or extra not in EXTRAS:
        return None, "Invalid size or extras option."
    if not 1 <= quantity <= 10:
        return None, "Quantity must be between 1 and 10."
    return (dish, size, extra, quantity), None


@app.route("/")
def home():
    dishes = [{"name": n, "serving": v[3]} for n, v in DISHES.items()]
    return render_template("index.html", dishes=dishes)


@app.route("/predict", methods=["POST"])
def predict():
    item, error = parse_item(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    result = predict_nutrition(model, *item)
    result.update({
        "dish": item[0],
        "daily_percent": round(result["total"] / DAILY_KCAL * 100, 1),
        "label": meal_label(result["total"]),
    })
    return jsonify(result)


@app.route("/report", methods=["POST"])
def report():
    """Download a JSON report for the whole plate (recalculated on the server)."""
    items = (request.get_json(silent=True) or {}).get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 20:
        return jsonify({"error": "Add at least one item to your plate."}), 400
    rows = []
    totals = {"kcal": 0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    for raw in items:
        item, error = parse_item(raw if isinstance(raw, dict) else {})
        if error:
            return jsonify({"error": error}), 400
        r = predict_nutrition(model, *item)
        rows.append({"dish": item[0], "size": item[1], "extra_oil": item[2],
                     "servings": item[3], "kcal": r["total"],
                     "protein_g": r["protein"], "carbs_g": r["carbs"], "fat_g": r["fat"]})
        totals["kcal"] += r["total"]
        totals["protein_g"] += r["protein"]
        totals["carbs_g"] += r["carbs"]
        totals["fat_g"] += r["fat"]
    for key in ("protein_g", "carbs_g", "fat_g"):
        totals[key] = round(totals[key], 1)
    body = json.dumps({"app": "Kolhapur Street Food Calorie Estimator",
                       "items": rows, "totals": totals,
                       "daily_percent": round(totals["kcal"] / DAILY_KCAL * 100, 1)}, indent=2)
    return Response(body, mimetype="application/json",
                    headers={"Content-Disposition": "attachment; filename=plate-report.json"})


@app.route("/dishes")
def dishes():
    """List the available dishes and what one serving means."""
    return jsonify([{"name": n, "serving": v[3]} for n, v in DISHES.items()])


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
