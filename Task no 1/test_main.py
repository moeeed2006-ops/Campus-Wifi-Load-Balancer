from main import allocate_resources, detect_congestion, predict_loads


def test_predict_loads_uses_trend():
    current = [50, 70]
    previous = [40, 60]
    predicted = predict_loads(current, previous)
    assert predicted[0] == 57.5
    assert predicted[1] == 77.5


def test_detect_congestion_flags_risky_zones():
    predicted = [70, 80, 50]
    flags = detect_congestion(predicted, threshold=75)
    assert flags.tolist() == [False, True, False]


def test_allocate_resources_sums_to_100():
    predicted = [40, 60]
    allocation = allocate_resources(predicted)
    assert round(allocation.sum(), 1) == 100.0
