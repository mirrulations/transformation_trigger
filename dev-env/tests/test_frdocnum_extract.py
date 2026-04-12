from lambda_functions.sql_docket_ingest.frdocnum_extract import collect_frdocnums


def test_collect_nested_and_both_key_names():
    data = {
        "a": 1,
        "items": [
            {"frdocnum": " 2024-1 ", "other": {"fdocnum": "2024-2"}},
        ],
        "fdocnum": "2024-3",
    }
    assert collect_frdocnums(data) == {"2024-1", "2024-2", "2024-3"}


def test_collect_empty_and_skips_null():
    assert collect_frdocnums({"frdocnum": None, "x": {"fdocnum": ""}}) == set()
