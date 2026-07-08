import json


with open(
    "knowledge_base/lab_ranges.json",
    encoding="utf-8"
) as f:

    data = json.load(f)



count = 0


for category, markers in data.items():

    for name, marker in markers.items():

        required = [
            "display_name",
            "aliases",
            "type",
            "sex_based",
            "age_based"
        ]


        for field in required:

            if field not in marker:

                print(
                    "Missing",
                    field,
                    "in",
                    name
                )


        count += 1



print(
    "Markers loaded:",
    count
)