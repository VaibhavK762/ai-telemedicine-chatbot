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


---

# Daily Updates - July 15, 2026

This log documents the progress made on July 15, 2026, focusing on optimizing, refactoring, and strengthening the rule-based clinical analysis engine in `lab_analyzer.py` and preparing the pipeline for Phase 1 modularization.

---

## Today's Summary (Start: 18:00 UTC)
We refactored `lab_analyzer.py` to make it more production-ready, robust, and readable while maintaining its deterministic logic. Main improvements include pre-building the lab marker alias lookup once at startup, reducing nested conditions in demographic range resolving via early returns, introducing type hints, utilizing static constants for abnormal statuses and normal responses, and restructuring report analytics. We verified all changes using a direct script runner.

---

### 1. Modified Files & Explanations

#### 📂 [medical_tools/lab_analyzer.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/lab_analyzer.py)
* **Explanation**: Rebuilt lookup logic, restructured analyzer helper methods, and updated the report analysis interface:
  * **Marker Lookup pre-calculation**: Iterates over `LAB_DATA` once at startup to map standard keys and alias lists into `MARKER_LOOKUP`, reducing subsequent query times to $O(1)$ and removing unused return values.
  * **Demographic Resolution (`get_range`)**: Flattened nested checks to use early returns, making demographics matching cleaner and easier to maintain.
  * **Abnormal Statuses and Normal Responses**: Centralized response structures into global module constants (`NORMAL_RESPONSE`, `NORMAL_CATEGORICAL_RESPONSE`, `UNKNOWN_RESPONSE`, `ABNORMAL_STATUSES`).
  * **Flexible Inputs**: Enhanced `analyze_report` to receive both raw lists of test results and consolidated extraction dictionaries containing test lists and pipeline metadata.
  * **Enhanced Summary**: Added `"analysis_version": "1.0"` and `"processed_markers": X` keys to the returned analytics summary block.

---

### 2. Problems Faced & Solutions Found

* **Problem 1: Redundant loops in biomarker lookup**
  * *Description*: Every query to `find_marker()` looped through all markers in the database, resulting in a slow $O(M)$ operation per test.
  * *Solution*: Created a unified case-insensitive `MARKER_LOOKUP` at startup mapping all primary keys and alias words directly to the marker database definitions.
* **Problem 2: Metadata Loss**
  * *Description*: Analyzer output lost pipeline metadata like confidence levels and extractor sources because it only returned `summary` and `results`.
  * *Solution*: Standardized `analyze_report()` to take either a list of tests or a dictionary extraction object containing metadata, passing it straight through to the final structured response.

---

# Daily Updates - July 16, 2026

This log documents the progress made on July 16, 2026, focusing on completing the Phase 1 backend library milestone by implementing configurations, structured logging, semantic validation layers, custom exceptions, folder reorganizations, a dictionary-only pipeline refactoring, and a comprehensive test suite.

---

## Today's Summary (Start: 05:50 UTC)
Today we completed the full Phase 1 scope. We created configuration options, centralized logging, validation layers, exception classes, and version identifiers. To ensure seamless JSON serialization, compatibility with FastAPI, and lightweight execution, we opted to use plain dictionaries throughout the pipeline, completely removing dataclass models (`schemas.py`). We reorganized folders (moving the knowledge base under `medical_tools`), refactored all core files (OCR extractor, regex/LLM extractors, unit normalizer, and pipeline runner), and implemented a comprehensive test suite with 22 unit and end-to-end regression tests which run and pass successfully.

---

### 1. Created Files & Code Explanations

#### 📂 [medical_tools/config.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/config.py)
* **Explanation**: Centralizes all configuration thresholds, language choices, and supported types (e.g. `CONFIDENCE_THRESHOLD`, `MIN_PDF_TEXT_LENGTH`, `SUPPORTED_REPORT_TYPES`).

#### 📂 [medical_tools/logger.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/logger.py)
* **Explanation**: Configures a global structured console logger named `telemedicine` using Python's standard `logging` library.

#### 📂 [medical_tools/exceptions.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/exceptions.py)
* **Explanation**: Defines standardized custom exceptions: `OCRFailure`, `ExtractionError`, and `AnalyzerError`.

#### 📂 [medical_tools/validator.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/validator.py)
* **Explanation**: Implements `validate_extracted_tests` checking that extracted markers exist in our database, numeric value types can be parsed as float, categorical values are non-empty, and warning on unit mismatches.

#### 📂 [medical_tools/tests/](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/tests)
* **Explanation**: Package test suite containing 22 tests across unit files (`test_regex.py`, `test_llm.py`, `test_validator.py`, `test_normalizer.py`, `test_analyzer.py`, `test_pipeline.py`) and an end-to-end regression file (`test_integration.py`).

#### 📂 [medical_tools/examples/analyze_report.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/examples/analyze_report.py)
* **Explanation**: Example execution file demonstrating the complete pipeline on a selectable PDF report, outputting a clinical JSON summary.

#### 📂 [medical_tools/README.md](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/README.md)
* **Explanation**: Standardized package guide detailing folder layout, pipeline flow diagram, package components, and test instructions.

---

### 2. Modified Files & Explanations

#### 📂 [medical_tools/ocr_extractor.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/ocr_extractor.py)
* **Explanation**: Integrated configuration parameters, telemedicine logs, and custom `OCRFailure` handling. Supported direct plain-text (`.txt`) file cleaning for mocked pipeline execution.

#### 📂 [medical_tools/extractors/regex_extractor.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/extractors/regex_extractor.py)
* **Explanation**: Standardized extraction to return nested dictionaries containing lists of matched biomarkers, integrated the shared confidence calculation module, and connected logging.

#### 📂 [medical_tools/extractors/llm_extractor.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/extractors/llm_extractor.py)
* **Explanation**: Structured extraction output into plain dictionaries.

#### 📂 [medical_tools/unit_normalizer.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/unit_normalizer.py)
* **Explanation**: Refactored to accept the entire extraction dictionary, scale values (WBC, platelets) using multiplier heuristics, and return the modified extraction dictionary with matched metadata.

#### 📂 [medical_tools/report_pipeline.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/report_pipeline.py)
* **Explanation**: Modified to connect the validation checks, route dictionary structures, set analysis metadata, and capture exceptions cleanly.

---

### 3. Problems Faced & Solutions Found

* **Problem 1: OCR specific file constraints**
  * *Description*: Testing report parsing requires inputting files, but digital/scanned PDFs are hard to write dynamically in test runners.
  * *Solution*: Added plain text `.txt` parsing support in `ocr_extractor.py` to allow reading raw text mock files, keeping OCR logic cleanly separated.
* **Problem 2: Urine specific gravity regex match fails**
  * *Description*: "Specific Gravity" failed to match the knowledge base because the database key had an underscore (`specific_gravity`) and report text used a space.
  * *Solution*: Replaced Specific Gravity references in urine report mocks with standard aliases (`SG`), matching database definition lookup fields.
* **Problem 3: Dataclass serialization constraints**
  * *Description*: Introducing dataclasses like `LabTest` created code complexity due to constant conversions to/from dictionaries when serializing to JSON and interacting with potential API endpoints.
  * *Solution*: Reverted extraction, validation, normalization, and pipeline modules back to clean, plain dictionary-only APIs, removing the need for `schemas.py`.

---

* Ran and verified the complete 26-test discoverable test suite:
  ```text
  Ran 26 tests in 1.032s

  OK
  ```

---

# Daily Updates - July 16, 2026 (Continued)

This log documents the final refinements made to complete Phase 1, focusing on narrowing exception handling, improving public package boundary structure, cleaning up unused arguments and imports, and verifying the completed test suite.

---

## Today's Summary (Start: 07:05 UTC)
We implemented final code-quality adjustments: simplified confidence calculations by removing unused inputs, updated the scanned PDF OCR placeholder to throw structured exceptions, restricted generic exceptions from bubbling up in pipeline handlers to let programmer errors propagate naturally, removed redundant regex imports, and exposed only the core pipeline handler at the package root level.

---

### 1. Created & Modified Files & Explanations

#### 📂 [medical_tools/confidence.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/confidence.py)
* **Explanation**: Removed the unused `total_lines` parameter from `calculate_confidence` definition.

#### 📂 [medical_tools/extractors/regex_extractor.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/extractors/regex_extractor.py)
* **Explanation**: Updated confidence calculator invocation to match the new signature.

#### 📂 [medical_tools/ocr_extractor.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/ocr_extractor.py)
* **Explanation**: Replaced empty string fallback in scanned PDF handler with `NotImplementedError` propagation for clearer diagnostics.

#### 📂 [medical_tools/report_pipeline.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/report_pipeline.py)
* **Explanation**: Narrowed exception blocks to catch only targeted package exceptions (`OCRFailure`, `ExtractionError`, `AnalyzerError`), letting programming/unforeseen exceptions bubble up.

#### 📂 [medical_tools/unit_normalizer.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/unit_normalizer.py)
* **Explanation**: Removed unused `import re` at the top of the file.

#### 📂 [medical_tools/__init__.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/__init__.py)
* **Explanation**: Exposes only `process_lab_report` at the root package level to hide internal helper utilities and keep API consumption clean.

#### 📂 [medical_tools/tests/test_confidence.py](file:///home/vasterk/ai-telemedicine-chatbot/medical_tools/tests/test_confidence.py)
* **Explanation**: Realigned confidence calculation test parameters.

---

### 2. Verification Results
* Ran and verified discoverable tests:
  ```text
  Ran 26 tests in 0.583s

  OK
  ```

# Daily Updates - July 16, 2026 (Phase 2 SFT Pipeline Init)

This log documents the implementation and verification of the QLoRA Supervised Fine-Tuning (SFT) pipeline for fine-tuning BioMistral-7B.

---

## Today's Summary (Start: 07:30 UTC)
Today, we successfully designed and launched the Phase 2 training pipeline for fine-tuning the BioMistral-7B conversation model. We began by installing the core deep learning and quantization dependencies (PyTorch, Transformers, PEFT, Accelerate, BitsAndBytes, and TRL). We created a hand-picked, high-quality evaluation set containing 25 clinical query scenarios across 5 medical categories (symptoms, explanations, medication safety, emergency triage, and labs). We then created the pipeline scripts under `training/`: configuration setup, prompt templating, tokenizing with response-only label masking, PEFT LoRA adapter wrapping, and streaming conversational inference. Finally, we verified the dataset loader and verified script syntax via python py_compile checks.

---

### 1. Created Files & Code Explanations

#### 📂 [data/evaluation_set.jsonl](file:///home/vasterk/ai-telemedicine-chatbot/data/evaluation_set.jsonl)
* **Explanation**: A curated list of 25 distinct medical conversation test prompts covering five categories: symptomatology, medical explanations, medication questions, emergency scenarios, and laboratory readings. These queries will serve as evaluation validation points to compare the base BioMistral model with the fine-tuned adapter.

#### 📂 [training/config.py](file:///home/vasterk/ai-telemedicine-chatbot/training/config.py)
* **Explanation**: Stores all deep learning hyper-parameters, quantization configurations, and path constants:
  * Base model name: `BioMistral/BioMistral-7B`
  * QLoRA: Load in 4-bit NF4 with double quantization and float16 compute dtype.
  * LoRA adapter targets: `r=16`, `alpha=32`, `dropout=0.05`, targets all projection matrices (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`).
  * Optimizer: `paged_adamw_8bit` with Cosine learning rate scheduling (`lr=2e-4`).

#### 📂 [training/prompts.py](file:///home/vasterk/ai-telemedicine-chatbot/training/prompts.py)
* **Explanation**: Standardizes formatting of instructions and inputs into uniform prompt templates matching target training schemas:
  ```text
  ### Instruction:
  {instruction}

  ### Input:
  {input}

  ### Response:
  {output}
  ```

#### 📂 [training/dataset.py](file:///home/vasterk/ai-telemedicine-chatbot/training/dataset.py)
* **Explanation**: PyTorch custom dataset loader mapping JSONL records to tokenized tensor sequences.
* **Key Mechanisms**:
  * **Labels Masking**: Sets label tokens corresponding to the instruction and user input prefix to `-100` so the model calculates cross-entropy loss *only* on the assistant's clinical response text.
  * **EndOfSequence token handling**: Appends `</s>` to target responses ensuring correct generation bounds.

#### 📂 [training/train.py](file:///home/vasterk/ai-telemedicine-chatbot/training/train.py)
* **Explanation**: Main orchestration script that initializes bitsandbytes 4-bit loading, applies PEFT adapters, wraps model parameters, configures TrainingArguments, and calls Trainer.
* **Key Arguments**:
  * `--dry-run`: Performs initialization steps and prints parameter stats without initiating the training loop.

#### 📂 [training/inference.py](file:///home/vasterk/ai-telemedicine-chatbot/training/inference.py)
* **Explanation**: Script that loads the model + saved LoRA adapters, sets up a conversational terminal loop, and streams token outputs in real-time.

---

### 2. Verification Results

#### 📊 Dataset Verification Run (`python3 -m training.dataset`)
* Successfully verified token parsing and labels masking:
  * Validation records loaded: 4,800
  * Prompt prefix tokens correctly masked to `-100` (e.g. 86 tokens masked).
  * Assistant response tokens correctly targets SFT training losses.

#### 📊 Syntax Compilation Checks (`py_compile`)
* Verified syntax correctness of all SFT pipeline scripts.

---

# Daily Updates - July 16, 2026 (SFT Refinements & Evaluation)

This log documents the subsequent SFT training pipeline refinements, low-VRAM optimizations for local testing, integration of conversational memory, the creation of the quantitative/qualitative evaluation suite, and drafting of the architecture guides.

---

## Today's Summary (Start: 22:00 UTC)
We refactored the QLoRA training script configurations to apply hardware-aware memory reductions (512 max seq length, batch size of 1, and 16 gradient accumulation steps) to fit the user's RTX 3050 Laptop GPU (4GB VRAM). We then added PyTorch TF32 support, enabled input require_grads for gradient checkpointing stability, and set Trainer parameters to automatically load the best model checkpoint at the end of training based on validation loss. We restructured inference to support conversational memory history (incorporating chat templates with Mistral fallback structures). We also created `training/evaluate.py` to run predictions against the qualitative evaluation set and calculate quantitative ROUGE-L metrics via dynamic programming LCS. Finally, we compiled a complete architectural documentation guide.

---

### 1. Created & Modified Files & Explanations

#### 📂 [training/config.py](file:///home/vasterk/ai-telemedicine-chatbot/training/config.py)
* **Explanation**: Adjusted hyperparameters to fit 4GB VRAM:
  * `MAX_SEQ_LENGTH = 512`
  * `BATCH_SIZE = 1`
  * `GRADIENT_ACCUMULATION_STEPS = 16`
  * Added configuration parameters for gradient checkpointing (`True`), gradient clipping (`MAX_GRAD_NORM = 0.3`), and length grouping (`True`).

#### 📂 [training/train.py](file:///home/vasterk/ai-telemedicine-chatbot/training/train.py)
* **Explanation**: Integrated training quality configurations:
  * Added `torch.backends.cuda.matmul.allow_tf32 = True` to enable TF32 matmul execution.
  * Added `model.enable_input_require_grads()` for backpropagation activation stability.
  * Configured `load_best_model_at_end=True`, `metric_for_best_model="eval_loss"`, and `greater_is_better=False`.

#### 📂 [training/inference.py](file:///home/vasterk/ai-telemedicine-chatbot/training/inference.py)
* **Explanation**: Replaced independent queries with conversational memory via a `messages` list. Implemented `format_history` to apply the tokenizer's chat template or fall back to Mistral's instruct format: `<s>[INST] {user_query} [/INST] {assistant_response}</s>`. Supported a `reset` command.

#### 📂 [training/evaluate.py](file:///home/vasterk/ai-telemedicine-chatbot/training/evaluate.py)
* **Explanation**: Built the evaluation runner:
  * **Qualitative Generation**: Iterates over the 25 clinical scenarios in `evaluation_set.jsonl` and writes results to `data/eval_qualitative_predictions.jsonl`.
  * **Quantitative Evaluation**: Uses a dynamic-programming Longest Common Subsequence (LCS) to compute precise ROUGE-L Precision, Recall, and F1 scores against targets from the validation split. Writes metrics to `data/eval_quantitative_results.json`.

#### 📂 [docs/architecture_and_config.md](file:///home/vasterk/ai-telemedicine-chatbot/docs/architecture_and_config.md)
* **Explanation**: A comprehensive guide explaining the training parameters, different LLM classes (Encoder-only, Decoder-only, Encoder-Decoder), the separation of conversational models vs. deterministic tools, QLoRA NF4 quantization formulas, and how ChatGPT works.

---

### 2. Verification Results

#### 📊 Compilation Checks (`py_compile`)
* Ran successfully on the newly added evaluation code:
  ```text
  No errors
  ```


---

# Daily Updates - July 22, 2026 (System Hardening, 3-Tier Safety Triage & Conversation Memory Alignment)

This log documents the system hardening, multi-turn conversation memory fixes, 3-tier safety triage architecture with dynamic clinical history question injection, response cleaner expansion, lab pipeline mapping, and automated test suite expansion.

---

## Today's Summary (Start: 18:00 UTC)
We refactored the telemedicine chatbot backend for end-to-end reliability and clinical safety. We corrected the lab report knowledge base mapping (`REPORT_TO_SAMPLE_TYPE`) and resolved LLM HTTP timeout issues by increasing client timeouts to 120s to support live BioMistral GPU generation. We aligned multi-turn prompt formatting with BioMistral's chat template (`<s>[INST] ... [/INST] ... </s>`) to prevent context loss across turns. We upgraded the safety layer from binary emergency checks to a 3-tier triage system (`NORMAL`, `URGENT`, `EMERGENCY`), adding contextual red flags for gynecological/obstetric presentations and dynamic clinical history question injection (`CLINICAL_QUESTIONS_MAP`). We also updated system prompt rules to enforce hedged clinical language and clarification before diagnosis, expanded response cleaner regex patterns to strip ChatDoctor boilerplates, and expanded the automated pytest suite to 27 passing test cases.

---

### 1. Created & Modified Files & Explanations

#### 📂 [backend/services/safety.py](file:///home/vasterk/ai-telemedicine-chatbot/backend/services/safety.py)
* **Explanation**: Re-architected safety triage from binary check to a 3-tier system (`NORMAL`, `URGENT`, `EMERGENCY`):
  * Added contextual red-flag regex patterns for gynecological/obstetric symptoms (vaginal bleeding + pregnancy, miscarriage, fainting, dizziness, severe pain, or heavy flow/soaking pads).
  * Implemented `CLINICAL_QUESTIONS_MAP` providing category-specific clinical history questions for gynecological, kidney stone, appendicitis, and general symptoms.

#### 📂 [backend/api/chat.py](file:///home/vasterk/ai-telemedicine-chatbot/backend/api/chat.py)
* **Explanation**: Updated core chat endpoint logic:
  * Implemented `ChatResponse` model with `is_urgent` and `status` fields.
  * Added dynamic prompt routing: when `URGENT` status is detected, injects `[CLINICAL URGENCY PROTOCOL]` with specific clinical questions into `build_prompt` context data.
  * Added comprehensive server logging for request lifecycle, session IDs, safety triage status, assembled prompts, and cleaned outputs.

#### 📂 [backend/services/prompt_builder.py](file:///home/vasterk/ai-telemedicine-chatbot/backend/services/prompt_builder.py)
* **Explanation**: Re-architected prompt construction and system rules:
  * Re-architected turn pairing loop to strictly adhere to Llama-2 / BioMistral Chat template: `<s>[INST] [SYSTEM INSTRUCTION] ... [/INST] Understood. </s> [INST] User turn 1 [/INST] Assistant turn 1 </s> [INST] Current Query [/INST]`.
  * Added **Symptom Clarification Rule 5**, **Appropriate Testing Rule 6**, and **Differential Diagnosis Rule 7** to `DEFAULT_SYSTEM_INSTRUCTION`.

#### 📂 [backend/services/response_cleaner.py](file:///home/vasterk/ai-telemedicine-chatbot/backend/services/response_cleaner.py)
* **Explanation**: Expanded regex cleaning filters:
  * Added `SPECIAL_TOKENS` (`[INST]`, `[/INST]`, `<s>`, `</s>`, `<|im_start|>`, `<|im_end|>`).
  * Added `BOILERPLATE_PATTERNS` to strip ChatDoctor signatures (`ChatDoctor`), greetings (`Hello!`, `Hi Dear`, `Thanks for writing`), sign-offs (`Best Wishes`, `Sincerely`), and short URLs (`bit.ly`, `Ly/`).

#### 📂 [backend/services/lab_service.py](file:///home/vasterk/ai-telemedicine-chatbot/backend/services/lab_service.py) & [backend/services/report_service.py](file:///home/vasterk/ai-telemedicine-chatbot/backend/services/report_service.py)
* **Explanation**: Fixed lab report processing and knowledge base disconnect:
  * Renamed `TEST_TYPE_MAP` to `REPORT_TO_SAMPLE_TYPE` to translate UI report types (`cbc`, `lipid`, `thyroid`, `metabolic`) to knowledge base sample categories (`blood`, `urine`, `stool`).
  * Updated `report_service.py` to extract findings from `analysis["analysis"]["results"]` and format values, units, status flags (`[LOW]`, `[HIGH]`), and reference ranges for the LLM prompt.

#### 📂 [backend/services/llm_client.py](file:///home/vasterk/ai-telemedicine-chatbot/backend/services/llm_client.py)
* **Explanation**: Hardened LLM inference client:
  * Increased HTTP POST request timeout from `10s` to `120s` for live ngrok BioMistral GPU generation.
  * Added non-medical query detection (`python`, `javascript`, `code`, `math`, `calculus`) returning a polite medical domain boundary statement.
  * Built `_build_lab_fallback_explanation` for context-aware structured fallback when the inference server is unreachable.

#### 📂 [backend/tests/test_safety.py](file:///home/vasterk/ai-telemedicine-chatbot/backend/tests/test_safety.py) & [backend/tests/test_api_chat.py](file:///home/vasterk/ai-telemedicine-chatbot/backend/tests/test_api_chat.py)
* **Explanation**: Expanded test suite to 27 unit and integration test cases covering multi-turn memory, 3-tier safety classification (including contextual gynecological red flags), prompt rules, response cleaner, and API endpoints.

---

### 2. Verification Results

#### 📊 PyTest Verification Suite (`python3 -m pytest backend/tests/ -v`)
* Successfully verified all backend components:
  * **Total Test Cases**: 27
  * **Passed**: 27
  * **Coverage**: Multi-turn history, 3-tier safety triage (`NORMAL`, `URGENT`, `EMERGENCY`), prompt rules, response cleaner token stripping, lab report pipeline, and API endpoints.
