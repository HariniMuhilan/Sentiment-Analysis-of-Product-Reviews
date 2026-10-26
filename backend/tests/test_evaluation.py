from app.nlp.evaluate import evaluate_predictions, run_evaluation_on_dataset

def test_evaluate_predictions_perfect():
    y_true = ["POSITIVE", "NEGATIVE", "NEUTRAL", "POSITIVE"]
    y_pred = ["POSITIVE", "NEGATIVE", "NEUTRAL", "POSITIVE"]
    res = evaluate_predictions(y_true, y_pred)
    assert res["total_samples"] == 4
    assert res["accuracy"] == 1.0
    assert res["macro_f1"] == 1.0
    assert res["per_class"]["POSITIVE"]["precision"] == 1.0
    assert res["confusion_matrix"]["POSITIVE"]["POSITIVE"] == 2

def test_evaluate_predictions_with_errors():
    y_true = ["POSITIVE", "POSITIVE", "NEGATIVE", "NEUTRAL"]
    y_pred = ["POSITIVE", "NEUTRAL", "NEGATIVE", "NEUTRAL"]
    res = evaluate_predictions(y_true, y_pred)
    assert res["total_samples"] == 4
    assert res["accuracy"] == 0.75
    assert res["macro_f1"] < 1.0
    assert res["confusion_matrix"]["POSITIVE"]["NEUTRAL"] == 1

def test_evaluation_endpoint(client):
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert "overall" in data
    assert "macro_f1" in data["overall"]
    assert "accuracy" in data["overall"]
    assert "confusion_matrix" in data["overall"]
    assert "model_name" in data
