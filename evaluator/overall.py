import sqlite3
import sys
from tqdm import tqdm

def calculate_overall_score(adherence, readability, accuracy):
    return (adherence + readability + accuracy) / 3

def update_table(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM evaluated")
    num_rows = cursor.fetchone()[0]

    cursor.execute("SELECT hash, human_adherence, human_readability, human_accuracy, ai_adherence, ai_readability, ai_accuracy FROM evaluated")
    records = cursor.fetchall()

    with tqdm(total=num_rows, desc="Updating scores", ncols=100) as pbar:
        for record in records:
            hash_id, human_adherence, human_readability, human_accuracy, ai_adherence, ai_readability, ai_accuracy = record
            human_overall = calculate_overall_score(human_adherence, human_readability, human_accuracy)
            ai_overall = calculate_overall_score(ai_adherence, ai_readability, ai_accuracy)

            cursor.execute("UPDATE evaluated SET human_overall = ?, ai_overall = ? WHERE hash = ?", (human_overall, ai_overall, hash_id))
            conn.commit()
            pbar.update(1)

    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_scores.py <path_to_database>")
        sys.exit(1)

    database_path = sys.argv[1]
    update_table(database_path)
