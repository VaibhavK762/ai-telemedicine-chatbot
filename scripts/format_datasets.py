import os
import json
import random
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

RAW = BASE_DIR / "data" / "raw"
OUT = BASE_DIR / "data" / "formatted"

OUT.mkdir(exist_ok=True)


SYSTEM_PROMPT = (
    "You are a safe medical assistant. "
    "Provide educational medical information, explain clearly, "
    "and recommend professional medical care when appropriate."
)


def save_jsonl(data, filename):
    path = OUT / filename

    with open(path, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Saved {len(data)} -> {filename}")


# -------------------------------------------------------
# 1. ChatDoctor
# -------------------------------------------------------

def format_chatdoctor(limit=70000):

    folder = RAW / "lavita chats"

    file = list(folder.glob("*.parquet"))[0]

    df = pd.read_parquet(file)

    rows = []

    for _, r in df.iterrows():

        inp = str(r["input"]).strip()
        out = str(r["output"]).strip()

        if len(inp) < 20 or len(out) < 50:
            continue

        rows.append({
            "source": "chatdoctor",
            "instruction": SYSTEM_PROMPT,
            "input": inp,
            "output": out
        })


    random.shuffle(rows)

    rows = rows[:limit]

    save_jsonl(rows, "chatdoctor.jsonl")



# -------------------------------------------------------
# 2. PubMedQA labelled
# -------------------------------------------------------

def format_pubmedqa():

    folder = RAW / "PubMedqa" / "PQA labelled"

    file = list(folder.glob("*.parquet"))[0]

    df = pd.read_parquet(file)


    rows = []

    for _, r in df.iterrows():

        question = str(r["question"]).strip()

        answer = str(r["long_answer"]).strip()

        decision = str(r["final_decision"]).strip()


        if not answer:
            continue


        output = (
            f"Conclusion: {decision}.\n\n"
            f"{answer}"
        )


        rows.append({
            "source": "pubmedqa",
            "instruction":
            "Answer the biomedical question using evidence-based reasoning.",
            "input": question,
            "output": output
        })


    save_jsonl(rows, "pubmedqa.jsonl")



# -------------------------------------------------------
# 3. MedQA
# -------------------------------------------------------

def format_medqa(limit=10000):

    folder = (
        RAW /
        "MedQA" /
        "data_clean" /
        "questions" /
        "US"
    )


    files = [
        folder / "train.jsonl",
        folder / "dev.jsonl"
    ]


    rows = []


    for file in files:

        with open(file, encoding="utf-8") as f:

            for line in f:

                r = json.loads(line)


                q = r["question"]

                options = r["options"]


                opts = "\n".join(
                    [
                    f"{k}: {v}"
                    for k, v in options.items()
                    ]
                )


                inp = (
                    q +
                    "\n\nOptions:\n" +
                    opts
                )


                out = (
                    "The most appropriate answer is "
                    f"{r['answer_idx']}: {r['answer']}."
                )


                rows.append({
                    "source": "medqa",
                    "instruction":
                    "Solve the medical question and provide the correct clinical answer.",
                    "input": inp,
                    "output": out
                })


    random.shuffle(rows)

    rows = rows[:limit]

    save_jsonl(rows, "medqa.jsonl")



# -------------------------------------------------------
# 4. MedMCQA
# -------------------------------------------------------

def format_medmcqa(limit=15000):

    folder = RAW / "MEDMCQs"

    files = list(folder.glob("*.parquet"))


    dfs = []

    for f in files:
        dfs.append(pd.read_parquet(f))


    df = pd.concat(dfs)


    rows = []


    option_map = {
        0:"opa",
        1:"opb",
        2:"opc",
        3:"opd"
    }


    for _, r in df.iterrows():

        if r["cop"] == -1:
            continue

        if r["choice_type"] != "single":
            continue


        exp = str(r["exp"]).strip()


        if len(exp) < 30:
            continue


        correct = option_map[int(r["cop"])]


        answer = r[correct]


        inp = f"""
{r['question']}

Options:
A: {r['opa']}
B: {r['opb']}
C: {r['opc']}
D: {r['opd']}
"""


        out = f"""
The correct answer is {answer}.

Explanation:
{exp}
"""


        rows.append({
            "source": "medmcqa",
            "instruction":
            "Answer the medical multiple choice question with reasoning.",
            "input": inp.strip(),
            "output": out.strip()
        })


    random.shuffle(rows)

    rows = rows[:limit]

    save_jsonl(rows, "medmcqa.jsonl")



# -------------------------------------------------------
# RUN EVERYTHING
# -------------------------------------------------------

if __name__ == "__main__":

    random.seed(42)


    format_chatdoctor()

    format_pubmedqa()

    format_medqa()

    format_medmcqa()


    print("\nFormatting completed.")