import json
import re
from ..lab_analyzer import LAB_DATA
from ..confidence import calculate_confidence
from ..logger import logger



def build_marker_lookup(test_type):
    lookup = {}
    markers = LAB_DATA.get(test_type, {})

    for key, info in markers.items():
        lookup[key.lower()] = {
            "marker": key,
            "display_name": info["display_name"],
            "unit": info.get("unit")
        }

        for alias in info.get("aliases", []):
            lookup[alias.lower()] = {
                "marker": key,
                "display_name": info["display_name"],
                "unit": info.get("unit")
            }

    return sorted(
        lookup.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )


def extract_value(line, alias):
    line = re.sub(
        rf"\b{re.escape(alias)}\b",
        "",
        line,
        count=1,
        flags=re.IGNORECASE
    )

    categorical = [
        "nil",
        "negative",
        "positive",
        "trace",
        "absent",
        "present",
        "+++",
        "++",
        "+"
    ]

    lower = line.lower()

    for value in categorical:
        if re.search(rf"\b{re.escape(value)}\b", lower):
            return value

    numbers = re.findall(r"\d+\.\d+|\d+", line)

    if not numbers:
        return None
    
    print(f"Extracted value {numbers[0]} from line: {line}")

    return float(numbers[0])


def regex_extract(text, test_type) -> dict:
    print("\n\n******** REGEX EXTRACTOR CALLED ********")
    print("TEST TYPE:", test_type)
    logger.info("Starting regex extraction for test type: %s", test_type)
    lookup = build_marker_lookup(test_type)

    print("=" * 60)
    print("TEST TYPE:", test_type)
    print("LOOKUP SIZE:", len(lookup))
    print("FIRST 20 LOOKUP ENTRIES")

    for alias, info in lookup[:20]:
        print(alias, "->", info["marker"])

    print("=" * 60)

    tests = []
    seen = set()
    alias_matches = 0
    duplicates = 0

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    print("=" * 60)
    print("OCR LINES")

    for i, line in enumerate(lines):
        print(f"{i}: {repr(line)}")

    print("=" * 60)

    for line in lines:
        clean = (
            line.lower()
            .replace("(", " ")
            .replace(")", " ")
        )

        for alias, info in lookup:
            pattern = rf"\b{re.escape(alias)}\b"

            if re.search(pattern, clean):
                print(f"MATCHED ALIAS: {alias}")    
                print(f"LINE: {line}")

            if not re.search(pattern, clean):
                continue

            alias_matches += 1
            value = extract_value(clean, alias)
            if value is None:
                break

            marker = info["marker"]

            if marker in seen:
                duplicates += 1
                break

            tests.append(
                {
                    "marker": marker,
                    "display_name": info["display_name"],
                    "value": value,
                    "unit": info["unit"]
                }
            )
            seen.add(marker)
            break

    confidence = calculate_confidence(
        alias_matches=alias_matches,
        extracted=len(tests),
        duplicates=duplicates
    )

    logger.info(
        "Regex extraction finished. Found %d markers. Confidence: %.2f (Alias matches: %d, Duplicates: %d)",
        len(tests),
        confidence,
        alias_matches,
        duplicates
    )

    return {
        "tests": tests,
        "metadata": {
            "source": "regex",
            "confidence": confidence,
            "markers_found": len(tests),
            "alias_matches": alias_matches,
            "duplicates": duplicates,
            "total_lines": len(lines)
        }
    }


if __name__ == "__main__":
    sample = """
    Hemoglobin 11.7
    RBC Count 4.36
    WBC Count 6.43
    Platelets 251
    """

    result = regex_extract(
        sample,
        "blood"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )