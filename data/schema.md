# Telemedicine AI Raw Datasets Schema

This file documents the schema, structure, size, and sample data for all the datasets located in the `data/raw/` directory.

---

## 1. MedQA (US)
* **Path**: `data/raw/MedQA/data_clean/questions/US/`
* **Format**: JSON Lines (`.jsonl`)
* **Total Records**: 12,723

### Files & Sizes
* **Train**: `train.jsonl` (10,178 records)
* **Dev**: `dev.jsonl` (1,272 records)
* **Test**: `test.jsonl` (1,273 records)

### Schema Fields
| Field | Type | Description |
| :--- | :--- | :--- |
| `question` | `string` | Clinical case vignette and the multiple-choice question. |
| `options` | `object` | Dictionary containing options `"A"`, `"B"`, `"C"`, `"D"`, `"E"`. |
| `answer` | `string` | Text content of the correct option. |
| `answer_idx` | `string` | The key of the correct option (`"A"`, `"B"`, `"C"`, `"D"`, or `"E"`). |
| `meta_info` | `string` | USMLE step level: `"step1"` or `"step2&3"`. |

### Example Record
```json
{
  "question": "A 23-year-old pregnant woman at 22 weeks gestation presents with burning upon urination. ... Which of the following is the best treatment for this patient?",
  "options": {
    "A": "Ampicillin",
    "B": "Ceftriaxone",
    "C": "Ciprofloxacin",
    "D": "Doxycycline",
    "E": "Nitrofurantoin"
  },
  "answer": "Nitrofurantoin",
  "answer_idx": "E",
  "meta_info": "step2&3"
}
```

---

## 2. PubMedQA
* **Path**: `data/raw/PubMedqa/`
* **Format**: Parquet (`.parquet`)
* **Total Records**: 212,269

### Files & Sizes
* **PQA Labelled**: `PQA labelled/train-00000-of-00001.parquet` (1,000 records)
* **PQA Artificial**: `PQA artificial/train-00000-of-00001 (1).parquet` (211,269 records)

### Schema Fields
| Field | Type | Description |
| :--- | :--- | :--- |
| `pubid` | `int32` | PubMed ID of the reference publication. |
| `question` | `string` | Yes/No/Maybe question derived from the title/abstract. |
| `context` | `object` | Struct containing the abstract structure:<br>- `contexts` (list of strings): Text segments of the abstract.<br>- `labels` (list of strings): Section labels (e.g. `BACKGROUND`, `RESULTS`).<br>- `meshes` (list of strings): Medical Subject Headings (MeSH). |
| `long_answer` | `string` | Abstract's detailed conclusion answering the question. |
| `final_decision` | `string` | Summary decision: `"yes"`, `"no"`, or `"maybe"`. |

### Example Record
```json
{
  "pubid": 21645374,
  "question": "Do mitochondria play a role in remodelling lace plant leaves during programmed cell death?",
  "context": {
    "contexts": [
      "Programmed cell death (PCD) is the regulated death of cells within an organism...",
      "The following paper elucidates the role of mitochondrial dynamics during..."
    ],
    "labels": ["BACKGROUND", "RESULTS"],
    "meshes": ["Alismataceae", "Apoptosis", "Cell Differentiation", "Mitochondria", "Plant Leaves"]
  },
  "long_answer": "Results depicted mitochondrial dynamics in vivo as PCD progresses within the lace plant... implicate the mitochondria as playing a critical and early role in developmentally regulated PCD in the lace plant.",
  "final_decision": "yes"
}
```

---

## 3. lavita chats
* **Path**: `data/raw/lavita chats/`
* **Format**: Parquet (`.parquet`)
* **Total Records**: 112,165

### Files & Sizes
* **Train**: `train-00000-of-00001-5e7cb295b9cff0bf.parquet` (112,165 records)

### Schema Fields
| Field | Type | Description |
| :--- | :--- | :--- |
| `instruction` | `string` | System/role instruction (e.g. *"If you are a doctor, please answer..."*). |
| `input` | `string` | Patient's description of their symptoms and clinical questions. |
| `output` | `string` | Medical professional's detailed consultation response and advice. |

### Example Record
```json
{
  "instruction": "If you are a doctor, please answer the medical questions based on the patient's description.",
  "input": "I woke up this morning feeling the whole room is spinning when i was sitting down. I went to the bathroom walking unsteadily, as i tried to focus i feel nauseous... By the way, if i lay down or sit down, my head do not spin...",
  "output": "Hi, Thank you for posting your query. The most likely cause for your symptoms is benign paroxysmal positional vertigo (BPPV)..."
}
```

---

## 4. MEDMCQs
* **Path**: `data/raw/MEDMCQs/`
* **Format**: Parquet (`.parquet`)
* **Total Records**: 193,155

### Files & Sizes
* **Train**: `train-00000-of-00001 (2).parquet` (182,822 records)
* **Validation**: `validation-00000-of-00001.parquet` (4,183 records)
* **Test**: `test-00000-of-00001.parquet` (6,150 records)

### Schema Fields
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `string` | Unique identifier for the question. |
| `question` | `string` | The multiple-choice question. |
| `opa` | `string` | Text for Option A. |
| `opb` | `string` | Text for Option B. |
| `opc` | `string` | Text for Option C. |
| `opd` | `string` | Text for Option D. |
| `cop` | `int64` | Index of the correct option (`0` for A, `1` for B, `2` for C, `3` for D, `-1` for unlabelled test). |
| `choice_type` | `string` | Type of choices selection: `"single"` or `"multi"`. |
| `exp` | `string` | Clinical explanation and references explaining why the choice is correct. |
| `subject_name` | `string` | Medical subject area (e.g. `Anatomy`, `Pathology`, `Physiology`). |
| `topic_name` | `string` | Subtopic classification name. |

### Example Record
```json
{
  "id": "e9ad821a-c438-4965-9f77-760819dfa155",
  "question": "Chronic urethral obstruction due to benign prostatic hyperplasia can lead to the following change in kidney parenchyma",
  "opa": "Hyperplasia",
  "opb": "Hyperophy",
  "opc": "Atrophy",
  "opd": "Dyplasia",
  "cop": 2,
  "choice_type": "single",
  "exp": "Chronic urethral obstruction because of urinary calculi... causes hydronephrosis... associated with progressive atrophy of the kidney...",
  "subject_name": "Anatomy",
  "topic_name": "Urinary tract"
}
```
