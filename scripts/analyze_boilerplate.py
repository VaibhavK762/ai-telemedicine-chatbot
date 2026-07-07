import json
import re
from pathlib import Path
from collections import Counter


BASE = Path(__file__).resolve().parents[1]

DATA = BASE / "data" / "formatted" / "chatdoctor.jsonl"


counter = Counter()


def split_sentences(text):

    sentences = re.split(
        r"[.!?]",
        text
    )

    return [
        s.strip().lower()
        for s in sentences
        if len(s.strip()) > 15
    ]



with open(DATA, encoding="utf-8") as f:

    for line in f:

        row = json.loads(line)

        output = row["output"]

        sentences = split_sentences(output)


        for s in sentences:

            counter[s] += 1



print("\nMost repeated sentences:\n")

for sent, count in counter.most_common(50):

    print(count, ":", sent)