# Daily Updates - July 7, 2026

This log documents the daily progress, files created/modified, code explanations, problems encountered, and solutions found.

---

## Today's Summary (Start: 14:40 UTC)
We started tracking progress today after setting up the directory architecture, cleaning up MedQA raw files, and establishing dataset schemas. The user added the primary dataset formatting scripts, logger utilities, test scripts, and updated the `.gitignore`. We executed and verified all scripts successfully.

Later in the session, the user implemented advanced preprocessing scripts: a boilerplate text analyzer, a cleaning script to scrub repetitive text structures, a deduplication utility, and a script to merge and split the dataset. These were run successfully and committed to the Git repository.

---

### 1. Created Files & Code Explanations

#### 📂 [scripts/format_datasets.py](file:///home/vasterk/ai-telemedicine-chatbot/scripts/format_datasets.py)
* **Explanation**: Processes raw dataset files (`ChatDoctor`, `PubMedQA`, `MedQA`, `MEDMCQs`) and converts them into a standardized instruction-following format required for QLoRA fine-tuning. Formatted datasets are outputted as `.jsonl` files in `data/formatted/`.
* **Key Functions**:
  * `save_jsonl(data, filename)`: Utility to serialize a list of dictionaries to JSON Lines format under `data/formatted/`.
  * `format_chatdoctor(limit=70000)`: Reads the `lavita chats` parquet file, filters out excessively short questions/answers, maps to the system prompt, shuffles, limits to 70k, and saves.
  * `format_pubmedqa()`: Processes the `PQA labelled` parquet dataset. Combines the `final_decision` (yes/no/maybe) and the `long_answer` (clinical reasoning) to form a complete output response.
  * `format_medqa(limit=10000)`: Merges MedQA US `train.jsonl` and `dev.jsonl` files, formats the clinical vignettes with multiple-choice options (`A` to `E`), formats correct index output, shuffles, limits to 10k, and saves.
  * `format_medmcqa(limit=15000)`: Concatenates `MEDMCQs` parquet partitions, filters for single-choice questions with explanation, maps the zero-indexed answer to the option key, constructs multiple-choice inputs, and formats output with explanation.

#### 📂 [scripts/analyze_boilerplate.py](file:///home/vasterk/ai-telemedicine-chatbot/scripts/analyze_boilerplate.py)
* **Explanation**: Analyzes the generated `chatdoctor.jsonl` formatted dataset to identify the most common repetitive boilerplate sentences (like closing templates, greetings, signatures) by splitting outputs into sentences and counting their frequencies.
* **Key Functions**:
  * `split_sentences(text)`: Splits text into sentences by punctuation (`.!?`), strips spaces, lowercases, and filters out sentences under 15 characters.
  * Main block: Iterates through the JSONL file, splits output fields into sentences, increments a `Counter` dictionary, and outputs the top 50 most repeated sentences.

#### 📂 [scripts/clean_data.py](file:///home/vasterk/ai-telemedicine-chatbot/scripts/clean_data.py)
* **Explanation**: Cleans the formatted datasets by removing common boilerplate structures, stripping HTML tags, normalized spacing, replacing broken unicode characters, and validating input/output sample lengths. Outputs cleaned files under `data/cleaned/`.
* **Key Functions**:
  * `normalize_text(text)`: Uses regex to strip HTML tags, normalizes whitespace to single spaces, and removes unicode replacement characters (`\uFFFD`).
  * `remove_boilerplate(text)`: Runs case-insensitive regex replacements for a pre-defined list of common closing templates, greetings, and signatures (such as *"thanks for using chat doctor"*).
  * `valid_sample(row)`: Filters out samples if they miss standard keys (`instruction`, `input`, `output`), have an input length < 10, an output length < 20, or a combined total string length > 8,000 characters.

#### 📂 [scripts/deduplicate.py](file:///home/vasterk/ai-telemedicine-chatbot/scripts/deduplicate.py)
* **Explanation**: Detects and removes duplicate question-answer pairs within each cleaned dataset file to prevent the model from overfitting on identical data. Outputs deduplicated files under `data/deduplicated/`.
* **Key Functions**:
  * `normalize_for_hash(text)`: Normalizes casing, whitespace, and strips text so minor differences in formatting don't bypass duplicate detection.
  * `make_hash(row)`: Computes an MD5 checksum of the combined normalized input and output.

#### 📂 [scripts/split_data.py](file:///home/vasterk/ai-telemedicine-chatbot/scripts/split_data.py)
* **Explanation**: Merges all preprocessed (cleaned + deduplicated) datasets in memory, shuffles the collective set, and splits it into final train, validation, and test datasets saved under `data/final/`.
* **Key Functions**:
  * `load_all()`: Aggregates all deduplicated records into a single list.
  * `save(data, name)`: Saves splits to JSON Lines files (`data/final/train.jsonl`, `data/final/validation.jsonl`, `data/final/test.jsonl`).
  * Main block: Performs a 90% train, 5% validation, and 5% test split on the shuffled aggregate set.

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

#### 📂 [knowledge_base/lab_ranges.json](file:///home/vasterk/ai-telemedicine-chatbot/knowledge_base/lab_ranges.json)
* **Explanation**: Touched by the user to ensure it is correctly initialized.

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
* **Problem 4: ChatDoctor dataset boilerplate**
  * *Description*: ChatDoctor dataset contained numerous repetitive chatbot signatures, links, and templates (e.g., "thanks for using chat doctor", "let me know if i can assist you further") which degrade response quality during LLM fine-tuning.
  * *Solution*: Created an analytical script (`analyze_boilerplate.py`) to discover the most frequent boilerplates, and implemented regex filters in a data cleaning script (`clean_data.py`) to scrub them out.

---

### 4. Git Actions & Commits
* Committed all tracked files (including logs, configs, utility scripts, and preprocessing files) to the local repository.
* **Commit details**:
  * Message: `"Data cleaning and split"`
  * Author: User
  * Status: clean working tree, local branch ahead of `origin/main` by 2 commits.

---

### 5. Verification Results

#### 📊 Formatting Stage (`format_datasets.py`)
* `chatdoctor.jsonl` saved: 70,000 records
* `pubmedqa.jsonl` saved: 1,000 records
* `medqa.jsonl` saved: 10,000 records
* `medmcqa.jsonl` saved: 15,000 records

#### 📊 Cleaning Stage (`clean_data.py`)
* `pubmedqa.jsonl`: kept 1000, removed 0
* `medqa.jsonl`: kept 10000, removed 0
* `medmcqa.jsonl`: kept 14995, removed 5 (due to length limits/empty fields)
* `chatdoctor.jsonl`: kept 69999, removed 1 (due to length limits/empty fields)

#### 📊 Deduplication Stage (`deduplicate.py`)
* Verified 0 duplicate samples found across any file.

#### 📊 Final Splitting Stage (`split_data.py`)
* Shuffled and split the merged dataset (total of **95,994** samples):
  * **train.jsonl**: 86,394 samples (90%)
  * **validation.jsonl**: 4,800 samples (5%)
  * **test.jsonl**: 4,800 samples (5%)

---

# Daily Updates - July 8, 2026

This log documents the progress made on July 8, 2026, focusing on implementing the lab report analysis functionality, validating reference ranges, and testing the system with clinical samples.

---

## Today's Summary (Start: 11:50 UTC)
Today, we initialized the laboratory analyzer tool and established database validation checks for reference ranges. The user populated the laboratory reference database (`knowledge_base/lab_ranges.json`) with 67 clinical markers across blood, urine, and stool tests. We added a parser-analyzer script, resolved key demographic-specific fallback issues, fixed redundant operations, and added robust parsing mechanisms for numeric inputs.

---

### 1. Created Files & Code Explanations

#### 📂 [medical_tools/lab_analyzer.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/lab_analyzer.py)
* **Explanation**: Parses and interprets patient lab result values by matching them against reference ranges defined in `knowledge_base/lab_ranges.json`. It handles demographic-specific ranges (by age/sex) and categorizes outputs into HIGH, LOW, NORMAL, ABNORMAL, or UNKNOWN statuses along with clinically relevant advice.
* **Key Functions**:
  * `find_marker(test_type, marker_name)`: Searches for a lab test marker under the specified category (case-insensitive) using its standard name or aliases to handle OCR spelling variations.
  * `get_range(marker, age=None, sex=None)`: Resolves the reference range dynamically. It checks flags for age-based and sex-based variations and falls back gracefully (sex/age -> sex-based -> age-based -> standard -> first key) depending on demographic parameters provided.
  * `analyze_numeric(marker, value, normal)`: Compares a numeric value against the resolved minimum and maximum bounds.
  * `analyze_categorical(marker, value)`: Matches text-based findings (e.g., "+", "++", "negative") against expected normal and abnormal arrays.
  * `analyze_lab(...)`: Coordinates the lookup, range resolving, numeric or categorical analysis, and packs metadata into the response.
  * `analyze_report(...)`: Iterates over multiple tests in a panel to compute a summary count (normal, abnormal, unknown) and compile the detailed individual results.

#### 📂 [scripts/validate_lab_json.py](file:///home/vasterk/ai-telemedicine-chatbot/scripts/validate_lab_json.py)
* **Explanation**: A verification script that loads the clinical reference ranges JSON database and validates that every entry conforms to the schema rules.
* **Key Functions**:
  * Loops through all test types (`blood`, `urine`, `stool`) and ensures every marker includes required properties: `display_name`, `aliases`, `type`, `sex_based`, and `age_based`.

---

### 2. Modified Files & Explanations

#### 📂 [knowledge_base/lab_ranges.json](file:///home/vasterk/ai-telemedicine-chatbot/knowledge_base/lab_ranges.json)
* **Explanation**: Expanded from an empty object to a comprehensive medical resource with 67 markers. Standardized schemas were created for all tests, including blood panel counts (hemoglobin, WBC, platelets), liver enzymes, lipid profiles, urine values, and stool panel indicators (FOBT, fecal calprotectin, H. pylori, consistency, etc.).

---

### 3. Problems Faced & Solutions Found

* **Problem 1: Lab Test Alias Mapping and OCR Variations**
  * *Description*: Patients or OCR tools may input lab test names in various formats (e.g., "Hb", "HGB", "Hemoglobin", or varying case). If matches are exact, the system will fail to identify the marker.
  * *Solution*: Implemented alias lists in `lab_ranges.json` and a case-insensitive check in `find_marker` that compares both the primary key and the aliases list.
* **Problem 2: Demographic Variations in Reference Ranges**
  * *Description*: Clinically, normal values for markers (e.g., hemoglobin or calprotectin) depend on sex and/or age.
  * *Solution*: Structured reference ranges to allow nested dict configurations (`ranges: {male: {...}, female: {...}}` or `ranges: {adult: {...}}`). Added robust waterfall logic in `get_range` to query matching ranges dynamically and fall back gracefully if age/sex attributes are omitted.
* **Problem 3: Redundant Function Invocation**
  * *Description*: We noticed that `analyze_lab` had a copy-paste bug where `analyze_numeric` was called twice in succession, overwriting the `result` variable redundantly.
  * *Solution*: Removed the duplicate call to optimize execution and keep code clean.
* **Problem 4: Numeric Conversion Failures for Non-Numeric Inputs**
  * *Description*: Passing non-numeric text inputs (e.g., "10 g/dL" instead of 10) to a numeric marker caused a `ValueError` in `float(value)` and crashed the analyzer.
  * *Solution*: Implemented a `try-except ValueError` wrapper around the float conversion in `analyze_lab`, returning a structured error response gracefully instead of crashing.

---

### 4. Git Actions & Commits
* None yet. Verified all files locally; files will be staged and committed upon session completion.

---

### 5. Verification Results

#### 📊 Database Integrity Check (`validate_lab_json.py`)
* Ran successfully and loaded **67** medical markers across blood, urine, and stool panels with zero missing schema fields.

#### 📊 Parser-Analyzer Validation (`lab_analyzer.py`)
* Verified execution against diverse test inputs:
  * **LDL-C (Blood, Numeric, High)**: Flagged 180 mg/dL as HIGH against reference range (0-100 mg/dL) with causes and follow-ups.
  * **Glucose (Blood, Numeric, Normal)**: Flagged 90 mg/dL as NORMAL against reference range (70-99 mg/dL).
  * **Urine Protein (Urine, Categorical, Abnormal)**: Matched "++" to `abnormal_values` list, returning ABNORMAL status.
  * **Report Summary**: Compiles panels (e.g., Hb, LDL-C, Glucose) yielding a JSON report summary with correct counts (`normal: 1`, `abnormal: 2`, `unknown: 0`).

---

# Daily Updates - July 9, 2026

This log documents the progress made on July 9, 2026, focusing on implementing PDF/image OCR extraction, text report parsing, integration of the diagnostic pipeline, and refinement of reference ranges.

---

## Today's Summary (Start: 12:00 UTC)
Today, we built the core components of the lab report extraction and processing pipeline. We implemented a unified OCR extraction layer capable of retrieving text from digital PDFs and scanned images/PDFs. We then developed a rule-based parser that maps extracted text to laboratory markers and handles unit normalizations. Finally, we updated `knowledge_base/lab_ranges.json` to expand search aliases and fix formatting, and verified the complete workflow against sample reports.

---

### 1. Created Files & Code Explanations

#### 📂 [medical_tools/ocr_extractor.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/ocr_extractor.py)
* **Explanation**: Handles text extraction from multi-format input files (selectable PDFs, images, and scanned PDFs).
* **Key Functions**:
  * `extract_pdf_text(file_path)`: Uses `pdfplumber` to extract digital text from selectable PDFs page-by-page.
  * `extract_image_text(file_path)`: Fallback method using PaddleOCR (`PaddleOCR`) to process images or scanned documents.
  * `extract_report_text(file_path)`: Inspects file extension and routes appropriately, falling back to empty string (or PaddleOCR in later steps) when selectable PDF text extraction fails/returns empty.

#### 📂 [medical_tools/report_parser.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/report_parser.py)
* **Explanation**: Extracts clinical test names and their corresponding numeric/categorical values from OCR or raw text inputs.
* **Key Functions**:
  * `build_marker_lookup(test_type)`: Dynamically generates a case-insensitive map of primary marker names and their alias synonyms to map OCR text lines back to canonical DB keys.
  * `extract_value(line, marker_alias)`: Extracts value matching categorical categories (e.g., negative, trace, positive, `+`, `++`) or falls back to using regex to isolate numeric readings after discarding the matched alias prefix.
  * `normalize_units(marker, value, line)`: Normalizes unit differences (e.g., scale adjustment for WBC count < 100 or platelets count < 1000).
  * `parse_report_text(text, test_type)`: Splits text into lines and compares each line against the alias lookup dictionary (sorted by length in descending order to avoid greedy substring matching) to output marker-value structures.

#### 📂 [medical_tools/report_pipeline.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/report_pipeline.py)
* **Explanation**: Serves as the main pipeline coordinator running the full lab report process.
* **Key Functions**:
  * `process_lab_report(text, test_type, age, sex)`: Connects text parsing (`parse_report_text`) with the clinical analyzer (`analyze_report`), outputting a consolidated JSON payload containing extracted test details and diagnostic analysis.

#### 📂 [test_reports/](file:///home/vasterk/ai-telemedicine-chatbot/test_reports)
* **Explanation**: Added a local test directory containing real-world sample reports (`blood_report.pdf` and `urine_report.pdf`) to verify extraction and analysis reliability.

---

### 2. Modified Files & Explanations

#### 📂 [knowledge_base/lab_ranges.json](file:///home/vasterk/ai-telemedicine-chatbot/knowledge_base/lab_ranges.json)
* **Explanation**: Enhanced reference range configurations and keyword mappings:
  * Expanded alias sets for markers like `Platelets` (added "Platelet Count"), `MCV` (added "(MCV)", "Mean corpuscular volume"), `MCH` (added "(MCH)", "Mean corpuscular hemoglobin"), `MCHC` (added "(MCHC)", "Mean corpuscular hemoglobin concentration"), `Urine Protein` (added "Proteins", "Urine Protein", "Albumin"), `Urine Glucose` (added "Glucose", "Urine Glucose", "Sugar"), `Urine RBC` (added "RBC", "RBCs", "Red Blood Cells", "Urine RBC").
  * Added additional normal/negative values mapping for Urine Glucose ("not detected") and Urine RBC ("nil", "none", "not seen").
  * Converted `urine_wbc` from categorical to a numeric type under unit `/hpf` with standard normal range bounds `0` - `5` and corresponding clinical interpretation text.

---

### 3. Problems Faced & Solutions Found

* **Problem 1: Selectable text vs scanned documents**
  * *Description*: Laboratory PDFs can either be digitally selectable or scanned images. Standard text parsing fails on image-based documents.
  * *Solution*: Implemented a fallback mechanism in `ocr_extractor.py` which detects if selectable text extraction returns empty or less than 50 characters, and routes the document to PaddleOCR to extract text visually.
* **Problem 2: UnboundLocalError during line parsing**
  * *Description*: The python pipeline crashed with `UnboundLocalError: cannot access local variable 'clean_line' where it is not associated with a value` in `parse_report_text` when iterating text strings.
  * *Solution*: Fixed local scope and loop variables in `medical_tools/report_parser.py` to ensure `clean_line` is properly initialized for all parsed text branches.
* **Problem 3: Greediness in short alias matches**
  * *Description*: Short aliases like "U" or "Hb" could accidentally match substrings inside other words (e.g., "u" in "unit", or "hb" inside "g/dl").
  * *Solution*: Refined parser regex to enforce boundary checks (`\b`) on aliases that are 3 characters or less, preventing incorrect marker matches.
* **Problem 4: WBC and Platelet Unit Scales**
  * *Description*: OCR text commonly displays WBC counts as 6.43 (meaning 6,430) and platelet counts as 251 (meaning 251,000). Comparing these directly against standard reference bounds (e.g., 4000-11000) causes incorrect "LOW" status diagnoses.
  * *Solution*: Added a unit normalization layer (`normalize_units` in `report_parser.py`) which scales values up by 1,000 when WBC is < 100 or Platelets is < 1,000.

---

### 4. Git Actions & Commits
* Verified files locally. Untracked files and modifications will be staged and committed.

---

### 5. Verification Results

#### 📊 Pipeline Integration Execution (`report_pipeline.py`)
* Ran the complete pipeline on `test_reports/blood_report.pdf` for a 46-year-old female:
  * Extracted values:
    * `hemoglobin`: 11.7 g/dL (LOW - Reference: 12.0 - 15.5)
    * `hematocrit`: 33.02% (LOW - Reference: 36 - 44)
    * `rbc_count`: 4.36 million/uL (NORMAL - Reference: 4.2 - 5.4)
    * `wbc_count`: 6,430.0 cells/uL (NORMAL - Reference: 4000 - 11000)
    * `platelets`: 251,000.0 cells/uL (NORMAL - Reference: 150000 - 450000)
  * Successfully flagged low Hemoglobin and Hematocrit, producing the correct structured JSON report and clinical recommendations.
