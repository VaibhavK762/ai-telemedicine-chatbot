import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

LAB_FILE = BASE_DIR / "knowledge_base" / "lab_ranges.json"


with open(LAB_FILE, encoding="utf-8") as f:
    LAB_DATA = json.load(f)



def find_marker(test_type, marker_name):
    """
    Finds marker using name or aliases.
    Handles OCR variations.
    """

    markers = LAB_DATA.get(test_type.lower())

    if not markers:
        return None, None


    query = marker_name.lower()


    for key, data in markers.items():

        names = [key.lower()]
        
        names += [
            alias.lower()
            for alias in data.get("aliases", [])
        ]


        if query in names:
            return key, data


    return None, None




def get_range(marker, age=None, sex=None):

    ranges = marker.get("ranges")


    if not ranges:
        return None


    # sex + age based
    if marker["sex_based"] and marker["age_based"]:

        if sex in ranges:

            sex_range = ranges[sex]

            if isinstance(sex_range, dict):

                if "adult" in sex_range:
                    return sex_range["adult"]


    # sex based
    if marker["sex_based"]:

        if sex in ranges:
            return ranges[sex]


    # age based
    if marker["age_based"]:

        if "adult" in ranges:
            return ranges["adult"]


    # standard
    if "standard" in ranges:
        return ranges["standard"]


    # fallback for names like:
    # optimal, fasting, adult etc.
    first_key = list(ranges.keys())[0]

    return ranges[first_key]





def analyze_numeric(marker, value, normal):


    if value < normal["min"]:

        return {
            "status": "LOW",
            "details": marker["low"]
        }


    elif value > normal["max"]:

        return {
            "status": "HIGH",
            "details": marker["high"]
        }


    else:

        return {
            "status": "NORMAL",
            "details": {
                "meaning":
                "Value is within reference range.",

                "possible_causes": [],

                "follow_up": []
            }
        }





def analyze_categorical(marker, value):

    value = str(value).lower()


    normal = [
        x.lower()
        for x in marker["normal_values"]
    ]


    abnormal = [
        x.lower()
        for x in marker["abnormal_values"]
    ]


    if value in normal:

        return {
            "status": "NORMAL",
            "details": {
                "meaning":
                "Finding is within normal limits.",

                "possible_causes": [],

                "follow_up": []
            }
        }


    if value in abnormal:

        return {
            "status": "ABNORMAL",
            "details": marker["positive"]
        }



    return {
        "status": "UNKNOWN",
        "details": {
            "meaning":
            "Could not interpret value.",

            "possible_causes": [],

            "follow_up": []
        }
    }




def analyze_lab(
        test_type,
        marker_name,
        value,
        age=None,
        sex=None
):


    key, marker = find_marker(
        test_type,
        marker_name
    )


    if marker is None:

        return {
            "error":
            "Marker not found"
        }



    if marker["type"] == "numeric":


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
        except ValueError:
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

            "marker":
            marker["display_name"],

            "value":
            value,

            "unit":
            marker["unit"],

            "normal_range":
            normal_range

        })


        return result



    else:


        result = analyze_categorical(
            marker,
            value
        )


        result.update({

            "marker":
            marker["display_name"],

            "value":
            value

        })


        return result


def analyze_report(
        test_type,
        tests,
        age=None,
        sex=None
):

    results = []

    summary = {
        "total_tests": 0,
        "normal": 0,
        "abnormal": 0,
        "unknown": 0
    }


    for test in tests:

        result = analyze_lab(
            test_type=test_type,
            marker_name=test["marker"],
            value=test["value"],
            age=age,
            sex=sex
        )


        results.append(result)


        summary["total_tests"] += 1


        status = result.get("status")


        if status == "NORMAL":

            summary["normal"] += 1


        elif status in [
            "LOW",
            "HIGH",
            "ABNORMAL"
        ]:

            summary["abnormal"] += 1


        else:

            summary["unknown"] += 1



    return {

        "summary": summary,

        "results": results
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