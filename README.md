# Telemedicine AI Project

This project contains the structure for a telemedicine chatbot, including data processing, model training, inference, medical tools, and safety classifiers.

## File Structure

```
telemedicine-ai/
├── data/
│   ├── raw/                 # HuggingFace downloads/cache copies
│   ├── formatted/           # converted instruction JSONL
│   └── final/               # train/val/test
│
├── scripts/
│   ├── download_data.py
│   ├── format_datasets.py
│   ├── clean_data.py
│   ├── deduplicate.py
│   ├── quality_check.py
│   └── split_data.py
│
├── knowledge_base/
│   ├── lab_ranges.json
│   └── drug_database.json
│
├── model/
│   ├── training/
│   │    └── qlora_train.ipynb
│   │
│   └── inference/
│        └── llama_server.py
│
├── api/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   └── utils/
│
├── medical_tools/
│   ├── lab_analyzer/
│   │    ├── ocr.py
│   │    ├── parser.py
│   │    └── analyzer.py
│   │
│   └── drug_checker/
│        ├── resolver.py
│        └── interactions.py
│
├── safety/
│   └── safety_classifier.py
│
├── frontend/
│
├── requirements.txt
└── README.md
```
