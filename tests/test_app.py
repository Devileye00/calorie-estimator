from app import app
from model import kcal_from_macros

client = app.test_client()


def post(dish="Vada Pav", size="Regular", extra="None", quantity=1):
    return client.post("/predict", json={"dish": dish, "size": size, "extra": extra, "quantity": quantity})


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_home_page_loads():
    res = client.get("/")
    assert res.status_code == 200
    assert b"Misal Pav" in res.data


def test_predict_returns_nutrition():
    data = post().get_json()
    assert {"total", "protein", "carbs", "fat", "label", "daily_percent"} <= set(data)


def test_vada_pav_close_to_database_value():
    assert 280 <= post().get_json()["total"] <= 330


def test_calories_follow_macro_formula():
    d = post("Pav Bhaji").get_json()
    expected = kcal_from_macros(d["protein"], d["carbs"], d["fat"])
    assert abs(d["total"] - expected) <= 2


def test_large_portion_has_more_calories():
    assert post(size="Large").get_json()["total"] > post(size="Small").get_json()["total"]


def test_extra_oil_adds_calories():
    assert post(extra="Lots").get_json()["total"] > post(extra="None").get_json()["total"]


def test_quantity_scales_total():
    one = post(quantity=1).get_json()["total"]
    three = post(quantity=3).get_json()["total"]
    assert abs(three - 3 * one) <= 3


def test_meal_label_heavy():
    assert post("Pav Bhaji", "Large", "Lots", 2).get_json()["label"] == "Heavy meal"


def test_invalid_dish_rejected():
    assert post(dish="Pizza").status_code == 400


def test_invalid_size_rejected():
    assert post(size="Huge").status_code == 400


def test_quantity_out_of_range_rejected():
    assert post(quantity=0).status_code == 400
    assert post(quantity=11).status_code == 400


def test_quantity_not_a_number_rejected():
    assert post(quantity="abc").status_code == 400


def test_missing_body_rejected():
    assert client.post("/predict").status_code == 400


def test_report_download():
    items = [{"dish": "Misal Pav", "size": "Regular", "extra": "None", "quantity": 1},
             {"dish": "Jalebi", "size": "Small", "extra": "None", "quantity": 1}]
    res = client.post("/report", json={"items": items})
    assert res.status_code == 200
    assert "attachment" in res.headers["Content-Disposition"]
    body = res.get_json()
    assert len(body["items"]) == 2
    assert body["totals"]["kcal"] == sum(i["kcal"] for i in body["items"])


def test_report_empty_plate_rejected():
    assert client.post("/report", json={"items": []}).status_code == 400


def test_report_invalid_item_rejected():
    bad = [{"dish": "Pizza", "size": "Regular", "extra": "None", "quantity": 1}]
    assert client.post("/report", json={"items": bad}).status_code == 400


def test_dishes_endpoint():
    res = client.get("/dishes")
    assert res.status_code == 200
    names = [d["name"] for d in res.get_json()]
    assert len(names) == 8
    assert "Misal Pav" in names


def test_custom_daily_goal_changes_percent():
    base = post().get_json()
    res = client.post("/predict", json={"dish": "Vada Pav", "size": "Regular", "extra": "None",
                                        "quantity": 1, "daily_goal": 1000})
    assert res.status_code == 200
    assert res.get_json()["daily_percent"] > base["daily_percent"]


def test_invalid_daily_goal_rejected():
    res = client.post("/predict", json={"dish": "Vada Pav", "size": "Regular", "extra": "None",
                                        "quantity": 1, "daily_goal": 50})
    assert res.status_code == 400
