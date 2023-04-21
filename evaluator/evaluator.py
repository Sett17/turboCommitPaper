import sqlite3
import argparse
import sys
import re
from typing import Optional, Dict
from tqdm import tqdm
import textstat
import spacy

def parse_arguments():
    parser = argparse.ArgumentParser(description='Evaluate commits in a SQLite database.')
    parser.add_argument('database', type=str, help='Path to the SQLite database file.')
    parser.add_argument('--reset', action='store_true', help='Delete the evaluated table and exit.')
    return parser.parse_args()

def create_evaluated_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evaluated (
        hash TEXT PRIMARY KEY,
        adherence_score REAL,
        readability_score REAL,
        accuracy_score REAL
    )
    ''')
    conn.commit()

def parse_commit_message(message: str) -> Optional[Dict[str, str]]:
    pattern = r'^(?P<type>\w+)(\((?P<scope>.+)\))?:\s(?P<message>[^\r\n]*)(?P<body>(?:\r?\n){2}[\s\S]*)?'
    match = re.match(pattern, message)

    if match:
        return match.groupdict()
    else:
        return None

nlp = spacy.load('en_core_web_sm')

def evaluate_pos(message: Optional[str]) -> float:
    if message is None:
        return 0.0

    doc = nlp(message)

    is_present_tense = False
    has_subject = False
    has_verb = False
    has_object = False

    for token in doc:
        if token.tag_ in {"VB", "VBP", "VBZ", "VBG"}:
            is_present_tense = True
        if token.dep_ == "nsubj":
            has_subject = True
        if token.pos_ == "VERB":
            has_verb = True
        if token.dep_ in {"dobj", "attr"}:
            has_object = True

    sentence_structure_score = 1.0 if has_subject and has_verb and has_object else 0.0
    tense_score = 1.0 if is_present_tense else 0.0

    combined_score = (sentence_structure_score + tense_score) / 2
    return combined_score

def evaluate_flesch(message: str) -> float:
    score = textstat.flesch_reading_ease(message)
    normalized_score = max(0, min(1, (score - 0) / (65 - 0)))
    return normalized_score

def delete_evaluated_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS evaluated')
    conn.commit()
    print('Deleted evaluated table.')

def main(database_path: str, reset: bool):
    conn = sqlite3.connect(database_path)

    if reset:
        delete_evaluated_table(conn)
        conn.close()
        return

    create_evaluated_table(conn)

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM commits')

    commits = cursor.fetchall()
    total_commits = len(commits)

    for commit in tqdm(commits, total=total_commits, desc="Evaluating commits", unit="commit"):
        parsed_message = parse_commit_message(commit[1])

        if parsed_message:
            adherence_score = 1.0
            pos_score = evaluate_pos(parsed_message['message'])

            if parsed_message['body']:
                flesch_score = evaluate_flesch(parsed_message['body'])
            else:
                flesch_score = evaluate_flesch(commit[1])
            readability_score = (pos_score + flesch_score) / 2
        else:
            adherence_score = 0.0
            pos_score = 0.0
            flesch_score = evaluate_flesch(commit[1])
            readability_score = flesch_score

        accuracy_score = None

        cursor.execute('INSERT INTO evaluated (hash, adherence_score, readability_score, accuracy_score) VALUES (?, ?, ?, ?)',
                       (commit[0], adherence_score, readability_score, accuracy_score))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    args = parse_arguments()
    main(args.database, args.reset)
