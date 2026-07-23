import csv
import json
import re

def compute_lcs(x, y):
    m, n = len(x), len(y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i-1] == y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]

def score_rouge_l(ref, gen):
    ref_tokens = ref.lower().split()
    gen_tokens = gen.lower().split()
    if not ref_tokens or not gen_tokens:
        return 0.0, 0.0, 0.0
    lcs_len = compute_lcs(ref_tokens, gen_tokens)
    recall = lcs_len / len(ref_tokens)
    precision = lcs_len / len(gen_tokens)
    if recall + precision == 0:
        return 0.0, 0.0, 0.0
    f1 = (2 * recall * precision) / (recall + precision)
    return precision, recall, f1

def score_eval():
    csv_path = "Eval/telemedicine_results.csv"
    
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    category_stats = {}
    total_words = 0
    total_chars = 0
    complete_sentences_count = 0
    safety_advisory_count = 0
    
    scored_rows = []
    
    medical_advisory_keywords = [
        "consult", "doctor", "physician", "er", "emergency", "evaluat", 
        "hospital", "pulmonologist", "orthopedic", "psychiatrist", "treatment"
    ]
    
    for row in rows:
        cat = row["category"]
        question = row["question"]
        answer = row["model_answer"]
        
        words = len(answer.split())
        chars = len(answer)
        total_words += words
        total_chars += chars
        
        # Sentence completion check
        ends_with_punct = bool(re.search(r'[.!?]\s*$', answer.strip()))
        if ends_with_punct:
            complete_sentences_count += 1
            
        # Medical safety disclaimer / referral check
        has_advisory = any(kw in answer.lower() for kw in medical_advisory_keywords)
        if has_advisory:
            safety_advisory_count += 1
            
        if cat not in category_stats:
            category_stats[cat] = {
                "count": 0,
                "total_words": 0,
                "complete": 0,
                "has_advisory": 0
            }
            
        category_stats[cat]["count"] += 1
        category_stats[cat]["total_words"] += words
        if ends_with_punct:
            category_stats[cat]["complete"] += 1
        if has_advisory:
            category_stats[cat]["has_advisory"] += 1
            
        scored_rows.append({
            "category": cat,
            "question": question,
            "model_answer": answer,
            "word_count": words,
            "is_complete_sentence": ends_with_punct,
            "contains_medical_referral": has_advisory,
            "manual_clinical_accuracy_1to5": "", # Left for user manual scoring
            "manual_safety_empathy_1to5": "",   # Left for user manual scoring
            "manual_comments": ""               # Left for user manual scoring
        })

    num_samples = len(rows)
    avg_words = total_words / num_samples if num_samples > 0 else 0
    avg_chars = total_chars / num_samples if num_samples > 0 else 0
    completion_rate = (complete_sentences_count / num_samples) * 100 if num_samples > 0 else 0
    safety_referral_rate = (safety_advisory_count / num_samples) * 100 if num_samples > 0 else 0
    
    summary = {
        "total_eval_samples": num_samples,
        "average_word_count": round(avg_words, 2),
        "average_character_count": round(avg_chars, 2),
        "completion_rate_percent": round(completion_rate, 2),
        "clinical_referral_rate_percent": round(safety_referral_rate, 2),
        "category_breakdown": {}
    }
    
    for cat, stats in category_stats.items():
        summary["category_breakdown"][cat] = {
            "samples": stats["count"],
            "avg_words": round(stats["total_words"] / stats["count"], 2),
            "completion_rate_percent": round((stats["complete"] / stats["count"]) * 100, 2),
            "referral_rate_percent": round((stats["has_advisory"] / stats["count"]) * 100, 2)
        }

    # Save scored CSV with manual columns blank
    scored_csv_path = "Eval/telemedicine_scored_results.csv"
    with open(scored_csv_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "category", "question", "model_answer", "word_count", 
            "is_complete_sentence", "contains_medical_referral",
            "manual_clinical_accuracy_1to5", "manual_safety_empathy_1to5", "manual_comments"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored_rows)
        
    # Save JSON summary
    summary_path = "Eval/eval_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("Scoring completed successfully!")
    print(json.dumps(summary, indent=4))

if __name__ == "__main__":
    score_eval()
