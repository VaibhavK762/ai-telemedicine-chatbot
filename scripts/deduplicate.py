import json
import hashlib
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_DIR = BASE_DIR / "data" / "deduplicated"

OUTPUT_DIR.mkdir(exist_ok=True)


def normalize_for_hash(text):
    """
    Normalize text so small spacing/case changes
    don't prevent duplicate detection.
    """

    return (
        text
        .lower()
        .strip()
        .replace("\n", " ")
        .replace("\t", " ")
    )


def make_hash(row):

    combined = (
        normalize_for_hash(row["input"])
        +
        normalize_for_hash(row["output"])
    )

    return hashlib.md5(
        combined.encode("utf-8")
    ).hexdigest()



def deduplicate_file(path):

    seen = set()

    kept = []
    removed = 0


    with open(
        path,
        encoding="utf-8"
    ) as f:


        for line in f:

            row = json.loads(line)

            h = make_hash(row)


            if h in seen:

                removed += 1
                continue


            seen.add(h)

            kept.append(row)



    output = OUTPUT_DIR / path.name


    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:

        for row in kept:

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
        f"kept {len(kept)}, "
        f"duplicates removed {removed}"
    )



if __name__ == "__main__":

    files = list(
        INPUT_DIR.glob("*.jsonl")
    )


    for file in files:

        deduplicate_file(file)


    print("\nDeduplication completed.")