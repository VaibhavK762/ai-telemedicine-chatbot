import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

LAB_FILE = BASE_DIR / "knowledge_base" / "lab_ranges.json"


with open(LAB_FILE, encoding="utf-8") as f:
    LAB_DATA = json.load(f)


# Build lookup once at startup
MARKER_LOOKUP = {}
for test_type, markers in LAB_DATA.items():
    test_type_lower = test_type.lower()
    MARKER_LOOKUP[test_type_lower] = {}
    for key, data in markers.items():
        MARKER_LOOKUP[test_type_lower][key.lower()] = data
        for alias in data.get("aliases", []):
            MARKER_LOOKUP[test_type_lower][alias.lower()] = data


NORMAL_RESPONSE = {
    "meaning": "Value is within reference range.",
    "possible_causes": [],
    "follow_up": []
}

NORMAL_CATEGORICAL_RESPONSE = {
    "meaning": "Finding is within normal limits.",
    "possible_causes": [],
    "follow_up": []
}

UNKNOWN_RESPONSE = {
    "meaning": "Could not interpret value.",
    "possible_causes": [],
    "follow_up": []
}

ABNORMAL_STATUSES = {
    "LOW",
    "HIGH",
    "ABNORMAL"
}


def find_marker(test_type: str, marker_name: str) -> dict | None:
    """
    Finds marker using name or aliases.
    Handles OCR variations.
    """
    return MARKER_LOOKUP.get(test_type.lower(), {}).get(marker_name.lower())





def get_range(
    marker: dict,
    age: int | None = None,
    sex: str | None = None
) -> dict | None:
    ranges = marker.get("ranges")
    if not ranges:
        return None

    # sex + age based
    if marker.get("sex_based") and marker.get("age_based") and sex in ranges:
        sex_range = ranges[sex]
        if isinstance(sex_range, dict) and "adult" in sex_range:
            return sex_range["adult"]

    # sex based
    if marker.get("sex_based") and sex in ranges:
        return ranges[sex]

    # age based
    if marker.get("age_based") and "adult" in ranges:
        return ranges["adult"]

    # standard
    if "standard" in ranges:
        return ranges["standard"]

    # fallback for names like:
    # optimal, fasting, adult etc.
    first_key = list(ranges.keys())[0]
    return ranges[first_key]


def analyze_numeric(
    marker: dict,
    value: float,
    normal: dict
) -> dict:
    if value < normal["min"]:
        return {
            "status": "LOW",
            "details": marker["low"]
        }

    if value > normal["max"]:
        return {
            "status": "HIGH",
            "details": marker["high"]
        }

    return {
        "status": "NORMAL",
        "details": NORMAL_RESPONSE
    }


def analyze_categorical(
    marker: dict,
    value: str | float | int | None
) -> dict:
    value_str = str(value).lower()

    normal = [
        x.lower()
        for x in marker.get("normal_values", [])
    ]

    abnormal = [
        x.lower()
        for x in marker.get("abnormal_values", [])
    ]

    if value_str in normal:
        return {
            "status": "NORMAL",
            "details": NORMAL_CATEGORICAL_RESPONSE
        }

    if value_str in abnormal:
        return {
            "status": "ABNORMAL",
            "details": marker["positive"]
        }

    return {
        "status": "UNKNOWN",
        "details": UNKNOWN_RESPONSE
    }


def analyze_lab(
    test_type: str,
    marker_name: str,
    value: str | float | int | None,
    age: int | None = None,
    sex: str | None = None
) -> dict:
    marker = find_marker(
        test_type,
        marker_name
    )

    if marker is None:
        return {
            "error": "Marker not found"
        }

    if marker.get("type") == "numeric":
        normal_range = get_range(
            marker,
            age,
            sex
        )
        if normal_range is None:
            return {
                "error": "No reference range available",
                "marker": marker["display_name"]
            }

        try:
            numeric_val = float(value)
        except (TypeError, ValueError):
            return {
                "error": "Value must be numeric",
                "marker": marker["display_name"],
                "value": value
            }

        result = analyze_numeric(
            marker,
            numeric_val,
            normal_range
        )

        result.update({
            "marker": marker["display_name"],
            "value": value,
            "unit": marker.get("unit"),
            "normal_range": normal_range
        })

        return result

    else:
        result = analyze_categorical(
            marker,
            value
        )

        result.update({
            "marker": marker["display_name"],
            "value": value
        })

        return result


def analyze_report(
    test_type: str,
    tests: dict | list,
    age: int | None = None,
    sex: str | None = None
) -> dict:
    if isinstance(tests, list):
        tests_list = tests
        metadata = {}
    else:
        tests_list = tests.get("tests", [])
        metadata = tests.get("metadata", {})

    results = []
    summary = {
        "total_tests": 0,
        "normal": 0,
        "abnormal": 0,
        "unknown": 0,
        "analysis_version": "1.0",
        "processed_markers": 0
    }

    for test in tests_list:
        result = analyze_lab(
            test_type=test_type,
            marker_name=test["marker"],
            value=test["value"],
            age=age,
            sex=sex
        )

        results.append(result)
        summary["total_tests"] += 1
        summary["processed_markers"] += 1

        status = result.get("status")
        if status == "NORMAL":
            summary["normal"] += 1
        elif status in ABNORMAL_STATUSES:
            summary["abnormal"] += 1
        else:
            summary["unknown"] += 1

    return {
        "summary": summary,
        "results": results,
        "metadata": metadata
    }


if __name__ == "__main__":
    report = [
        {
            "marker": "Hb",
            "value": 10
        },
        {
            "marker": "LDL-C",
            "value": 180
        },
        {
            "marker": "Glucose",
            "value": 90
        }
    ]

    result = analyze_report(
        test_type="blood",
        tests=report,
        age=25,
        sex="male"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )