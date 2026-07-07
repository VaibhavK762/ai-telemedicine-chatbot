import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = BASE_DIR / "data" / "formatted"
OUTPUT_DIR = BASE_DIR / "data" / "cleaned"

OUTPUT_DIR.mkdir(exist_ok=True)


MAX_CHARS = 8000      # approx <2048 tokens
MIN_INPUT = 10
MIN_OUTPUT = 20


REMOVE_PHRASES = [

    # ChatDoctor branding
    "thanks for using chat doctor",
    "thanks for your question on chat doctor",
    "welcome to chat doctor",
    "hi, welcome to chat doctor",
    "i am chat doctor answering your query",

    # closing templates
    "let me know if i can assist you further",
    "hope i have answered your query",
    "hope i have solved your query",
    "hope this answers your query",
    "hope i have answered your question",
    "wish you good health",
    "wishing you good health",
    "wish you a very good health",
    "wish you a good health",
    "take care chat doctor",

    # follow-up boilerplate
    "i will be happy to help you further",
    "i will be happy to answer your queries",
    "please do not hesitate to ask in case of any further doubts",
    "if you have additional questions or follow-up queries then please do not hesitate in writing to us",

    # signatures
    "regards chat doctor",
    "thanks and regards",
    "available for further clarifications",

    # corrupted
    "hi, dairy have gone through your question",
    "degree understand your concerns went through your details",

    # links
    "if you require more of my help in this aspect, please use this url"
]


def normalize_text(text):

    if not text:
        return ""

    text = str(text)


    # remove html
    text = re.sub(
        r"<.*?>",
        "",
        text
    )


    # remove weird spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )


    # remove broken unicode symbols
    text = (
        text
        .replace("\uFFFD", "")
        .strip()
    )


    return text



def remove_boilerplate(text):

    for phrase in REMOVE_PHRASES:

        pattern = re.compile(
            re.escape(phrase),
            flags=re.IGNORECASE
        )

        text = pattern.sub(
            "",
            text
        )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()



def valid_sample(row):

    required = [
        "instruction",
        "input",
        "output"
    ]


    for key in required:

        if key not in row:
            return False


    if len(row["input"]) < MIN_INPUT:
        return False


    if len(row["output"]) < MIN_OUTPUT:
        return False


    total_length = (
        len(row["instruction"])
        +
        len(row["input"])
        +
        len(row["output"])
    )


    if total_length > MAX_CHARS:
        return False


    return True



def clean_file(path):

    cleaned = []

    removed = 0


    with open(
        path,
        encoding="utf-8"
    ) as f:


        for line in f:

            row = json.loads(line)


            row["instruction"] = normalize_text(
                row["instruction"]
            )


            row["input"] = normalize_text(
                row["input"]
            )


            row["output"] = normalize_text(
                row["output"]
            )


            row["output"] = remove_boilerplate(
                row["output"]
            )


            if valid_sample(row):

                cleaned.append(row)

            else:

                removed += 1



    out_file = OUTPUT_DIR / path.name


    with open(
        out_file,
        "w",
        encoding="utf-8"
    ) as f:


        for row in cleaned:

            f.write(
                json.dumps(
                    row,
                    ensure_ascii=False
                )
                +
                "\n"
            )



    print(
        f"{path.name}: "
        f"kept {len(cleaned)}, "
        f"removed {removed}"
    )



if __name__ == "__main__":


    files = list(
        INPUT_DIR.glob("*.jsonl")
    )


    for file in files:

        clean_file(file)


    print("\nCleaning completed.")