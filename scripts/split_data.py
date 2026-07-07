import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = BASE_DIR / "data" / "deduplicated"
OUTPUT_DIR = BASE_DIR / "data" / "final"

OUTPUT_DIR.mkdir(exist_ok=True)

random.seed(42)
def load_all():

    data = []

    for file in INPUT_DIR.glob("*.jsonl"):

        with open(file, encoding="utf-8") as f:

            for line in f:

                data.append(
                    json.loads(line)
                )

    return data

def save(data, name):

    path = OUTPUT_DIR / name

    with open(path, "w", encoding="utf-8") as f:

        for row in data:

            f.write(
                json.dumps(
                    row,
                    ensure_ascii=False
                )
                + "\n"
            )
    print(
        name,
        len(data)
    )

if __name__ == "__main__":

    data = load_all()

    print(
        "Total samples:",
        len(data)
    )

    random.shuffle(data)
    n = len(data)

    train_end = int(
        n * 0.90
    )
    val_end = int(
        n * 0.95
    )

    train = data[:train_end]
    val = data[train_end:val_end]
    test = data[val_end:]

    save(
        train,
        "train.jsonl"
    )

    save(
        val,
        "validation.jsonl"
    )

    save(
        test,
        "test.jsonl"
    )
    print("\nSplit completed.")