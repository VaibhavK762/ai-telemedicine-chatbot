import re
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

LAB_FILE = BASE_DIR / "knowledge_base" / "lab_ranges.json"


with open(LAB_FILE, encoding="utf-8") as f:
    LAB_DATA = json.load(f)



def build_marker_lookup(test_type):

    lookup = {}

    markers = LAB_DATA[test_type]


    for key, info in markers.items():


        lookup[key.lower()] = key


        for alias in info.get(
            "aliases",
            []
        ):

            lookup[
                alias.lower()
            ] = key


    return lookup

def extract_number(text, marker_name=None):

    line = text


    if marker_name:

        line = line.replace(
            marker_name.lower(),
            "",
            1
        )


    numbers = re.findall(
        r"\d+\.\d+|\d+",
        line
    )


    if not numbers:
        return None


    return float(numbers[0])

def normalize_units(marker, value, line):


    if marker == "wbc_count":

        if value < 100:

            return value * 1000


    if marker == "platelets":

        if value < 1000:

            return value * 1000


    return value

    # Platelets commonly lakh/uL

    if marker == "platelets":

        if (
            "lakh" in line.lower()
            or "10^5" in line
        ):

            return value * 100000


    return value


def parse_report_text(text, test_type):

    MARKER_LOOKUP = build_marker_lookup(test_type)

    """
    Converts OCR text into marker/value pairs.
    """

    results = []
    seen = set()
    MARKER_LOOKUP = build_marker_lookup(
        test_type
    )

    lines = text.split("\n")

    
    for line in lines:


        clean_line = (
            line
            .lower()
            .strip()
        )


        if not clean_line:
            continue



        for alias, marker in sorted(
            MARKER_LOOKUP.items(),
            key=lambda x: len(x[0]),
            reverse=True
        ):

                alias_clean = alias.lower()


                if len(alias_clean) <= 3:

                    matched = re.search(
                        r"\b" + re.escape(alias_clean) + r"\b",
                        clean_line
                    )
                else:
                    matched = alias_clean in clean_line


                if matched:


                    value = extract_value(
                        clean_line,
                        alias
                    )


                    value = normalize_units(
                        marker,
                        value,
                        clean_line
                    )


                    if value is not None:


                        if marker not in seen:

                            results.append(
                                {
                                    "marker": marker,
                                    "value": value
                                }
                            )


                            seen.add(marker)


                    break


    return results



def extract_value(line, marker_alias=None):


    categories = [
        "nil",
        "negative",
        "positive",
        "trace",
        "absent",
        "present",
        "+",
        "++",
        "+++"
    ]


    lower = line.lower()


    for item in categories:

        if item in lower:

            return item


    # remove marker name before finding numbers
    # prevents Hb/RBC aliases affecting extraction

    if marker_alias:

        lower = lower.replace(
            marker_alias.lower(),
            "",
            1
        )


    numbers = re.findall(
        r"\d+\.\d+|\d+",
        lower
    )


    if not numbers:

        return None


    return float(numbers[0])

if __name__ == "__main__":


    sample = """

    Hemoglobin    10 g/dL
    LDL-C         180 mg/dL
    Glucose       90 mg/dL

    """


    result = parse_report_text(
        sample
    )


    print(
        json.dumps(
            result,
            indent=4
        )
    )