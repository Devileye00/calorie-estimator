"""Calorie model for Kolhapur street food.

Each dish has typical macronutrient values per regular serving
(protein, carbohydrate, fat in grams). A RandomForest regressor learns how
portion size and extra oil/butter change these macros, and calories are then
calculated with the standard Atwater formula:

    kcal = 4 x protein + 4 x carbs + 9 x fat

Data notes: Vada Pav values follow the FatSecret database entry (1 piece,
140 g). Other dishes use typical published values for a standard street-food
serving. Real calories vary with recipe, so treat results as estimates.
"""
import os
import random

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# dish -> (protein g, carbs g, fat g, serving description)
DISHES = {
    "Misal Pav":        (15.0, 60.0, 20.0, "1 plate with 2 pav, ~300 g"),
    "Vada Pav":         (9.2,  40.2, 11.9, "1 piece, ~140 g"),
    "Pav Bhaji":        (12.0, 72.0, 20.0, "1 plate with 2 pav, ~350 g"),
    "Samosa":           (4.0,  24.0, 17.0, "1 piece, ~100 g"),
    "Jalebi":           (2.0,  70.0, 11.0, "100 g"),
    "Masala Dosa":      (8.0,  55.0, 15.0, "1 dosa, ~200 g"),
    "Bhel Puri":        (6.0,  48.0,  8.0, "1 plate, ~150 g"),
    "Sabudana Khichdi": (5.0,  55.0, 14.0, "1 plate, ~200 g"),
}
SIZES = {"Small": 0.75, "Regular": 1.0, "Large": 1.3}
# extra oil / butter / farsan -> extra grams of fat added to the serving
EXTRAS = {"None": 0.0, "Some": 5.0, "Lots": 12.0}

DISH_LIST = list(DISHES)


def encode(dish, size, extra):
    row = [1.0 if dish == d else 0.0 for d in DISH_LIST]
    row.append(SIZES[size])
    row.append(EXTRAS[extra])
    return row


def kcal_from_macros(protein, carbs, fat):
    return 4 * protein + 4 * carbs + 9 * fat


def build_dataset(seed=42):
    rnd = random.Random(seed)
    X, y = [], []
    for dish, (p, c, f, _) in DISHES.items():
        for size, factor in SIZES.items():
            for extra, extra_fat in EXTRAS.items():
                target = [p * factor, c * factor, f * factor + extra_fat]
                for _ in range(20):
                    X.append(encode(dish, size, extra))
                    y.append([v * rnd.uniform(0.96, 1.04) for v in target])
    return np.array(X), np.array(y)


def train():
    X, y = build_dataset()
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return model


def load_model():
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            pass  # saved with another library version: retrain
    return train()


def predict_nutrition(model, dish, size, extra, quantity):
    """Return per-serving and total nutrition for the chosen meal."""
    p, c, f = (float(v) for v in model.predict([encode(dish, size, extra)])[0])
    per_serving = round(kcal_from_macros(p, c, f))
    return {
        "per_serving": per_serving,
        "total": round(kcal_from_macros(p, c, f) * quantity),
        "protein": round(p * quantity, 1),
        "carbs": round(c * quantity, 1),
        "fat": round(f * quantity, 1),
    }


if __name__ == "__main__":
    train()
    print("Model trained and saved to", MODEL_PATH)
