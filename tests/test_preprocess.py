from src.model.preprocess import analyze_dataset_quality


def test_dataset_quality_analysis():
    stats = analyze_dataset_quality(
        ["abc", "abcd", "abcd", "password123"]
    )

    assert stats["count"] == 4
    assert stats["min_length"] == 3
    assert stats["max_length"] == 11
    assert stats["unique_ratio"] == 0.75


def test_dataset_quality_empty_input():
    stats = analyze_dataset_quality([])

    assert stats["count"] == 0
    assert stats["unique_ratio"] == 0