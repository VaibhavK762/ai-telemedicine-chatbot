# Daily Updates - July 7, 2026

This log documents the daily progress, files created/modified, code explanations, problems encountered, and solutions found.

---

## Today's Summary (Start: 14:40 UTC)
We started tracking progress today after setting up the directory architecture, cleaning up MedQA raw files, and establishing dataset schemas. The user added the primary dataset formatting scripts, logger utilities, test scripts, and updated the `.gitignore`. We executed and verified all scripts successfully.

### 1. Created Files & Code Explanations

#### 📂 [scripts/format_datasets.py](file:///home/vasterk/ai-telemedicine-chatbot/scripts/format_datasets.py)
* **Explanation**: Processes raw dataset files (`ChatDoctor`, `PubMedQA`, `MedQA`, `MEDMCQs`) and converts them into a standardized instruction-following format required for QLoRA fine-tuning. Formatted datasets are outputted as `.jsonl` files in `data/formatted/`.
* **Key Functions**:
  * `save_jsonl(data, filename)`: Utility to serialize a list of dictionaries to JSON Lines format under `data/formatted/`.
  * `format_chatdoctor(limit=70000)`: Reads the `lavita chats` parquet file, filters out excessively short questions/answers, maps to the system prompt, shuffles, limits to 70k, and saves.
  * `format_pubmedqa()`: Processes the `PQA labelled` parquet dataset. Combines the `final_decision` (yes/no/maybe) and the `long_answer` (clinical reasoning) to form a complete output response.
  * `format_medqa(limit=10000)`: Merges MedQA US `train.jsonl` and `dev.jsonl` files, formats the clinical vignettes with multiple-choice options (`A` to `E`), formats correct index output, shuffles, limits to 10k, and saves.
  * `format_medmcqa(limit=15000)`: Concatenates `MEDMCQs` parquet partitions, filters for single-choice questions with explanation, maps the zero-indexed answer to the option key, constructs multiple-choice inputs, and formats output with explanation.

#### 📂 [utils/logger.py](file:///home/vasterk/ai-telemedicine-chatbot/utils/logger.py)
* **Explanation**: Implements a global logging configuration for logging application events, data loading, warnings, and errors.
* **Code Details**:
  * Sets up folder `logs/` dynamically.
  * Uses `logging.basicConfig` to establish a custom format: `%(asctime)s | %(levelname)s | %(name)s | %(message)s`.
  * Configures two logging handlers: `FileHandler` (saving to `logs/app.log`) and `StreamHandler` (outputting to terminal/stdout).

#### 📂 [log.py](file:///home/vasterk/ai-telemedicine-chatbot/log.py)
* **Explanation**: Simple test entry point script verifying that the custom logger utility handles levels properly and outputs correct formatting to both the console and file.

---

### 2. Modified Files & Explanations

#### 📂 [.gitignore](file:///home/vasterk/ai-telemedicine-chatbot/.gitignore)
* **Explanation**: Updated to support structured ignores across all stages of development:
  * Excludes large datasets (`data/raw/`, `data/final/`, `.parquet`, `.jsonl`, `.csv`, `.zip`).
  * Explicitly preserves directories structure via `!data/.../.gitkeep`.
  * Excludes ML checkpoints (`models/`, `*.safetensors`, `*.pt`, `*.gguf`).
  * Excludes logs, IDE structures, caches (`.cache/`, `.vscode/`, `logs/`, `*.log`).

---

### 3. Problems Faced & Solutions Found

* **Problem 1: Dataset processing dependencies**
  * *Description*: The python environment did not have `pandas` and `pyarrow` installed initially, which prevented reading the `.parquet` formatted datasets.
  * *Solution*: Installed `pandas` and `pyarrow` inside the active virtual environment using `pip` inside the virtual environment (`venv/bin/pip install pandas pyarrow`).
* **Problem 2: Nested data directories**
  * *Description*: Raw MedQA files were extracted inside a double-nested `data_clean/data_clean` structure.
  * *Solution*: Flattened the structure by moving files up one level and removing the empty directory.
* **Problem 3: Missing packages warnings**
  * *Description*: The formatting script completed successfully, but we needed to ensure logs were routed correctly.
  * *Solution*: Executed and validated the newly created logging setup, verifying that logs write to both stdout and `logs/app.log`.

---

### 4. Verification Results
* Running `scripts/format_datasets.py` completed successfully:
  * `chatdoctor.jsonl` saved: 70,000 records
  * `pubmedqa.jsonl` saved: 1,000 records
  * `medqa.jsonl` saved: 10,000 records
  * `medmcqa.jsonl` saved: 15,000 records
* Running `log.py` correctly printed logging messages in the desired format to stdout and stored them under `logs/app.log`.
