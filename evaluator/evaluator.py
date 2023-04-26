import sqlite3
import argparse
import sys
import re
from typing import Optional, Dict
from tqdm import tqdm
import textstat
import spacy

def create_evaluated_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evaluated (
        hash TEXT PRIMARY KEY,
        human_adherence REAL,
        human_readability REAL,
        human_accuracy REAL,
        human_overall REAL,
        ai_adherence REAL,
        ai_readability REAL,
        ai_accuracy REAL,
        ai_overall REAL
    )
    ''')
    conn.commit()

def insert_evaluated(conn: sqlite3.Connection, hash: str, human_scores: Dict[str, float], ai_scores: Dict[str, float]):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO evaluated (
        hash, 
        human_adherence, human_readability, human_accuracy, human_overall,
        ai_adherence, ai_readability, ai_accuracy, ai_overall
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        hash,
        human_scores['adherence'], human_scores['readability'], human_scores['accuracy'], human_scores.get('overall'),
        ai_scores['adherence'], ai_scores['readability'], ai_scores['accuracy'], ai_scores.get('overall')
    ))
    conn.commit()

def update_overall_scores(conn: sqlite3.Connection, hash: str, human_overall: Optional[float], ai_overall: Optional[float]):
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE evaluated
    SET human_overall = ?, ai_overall = ?
    WHERE hash = ?
    ''', (human_overall, ai_overall, hash))
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

def evaluate_commit(commit) -> Dict[str, Optional[float]]:
    # hash, message, _ = commit
    hash = commit[0]
    message = commit[1]
    
    parsed_message = parse_commit_message(message)

    if parsed_message:
        adherence_score = 1.0
        pos_score = evaluate_pos(parsed_message['message'])
        if parsed_message['body']:
            flesch_score = evaluate_flesch(parsed_message['body'])
        else:
            flesch_score = evaluate_flesch(parsed_message['message'])
        readability_score = (pos_score + flesch_score) / 2
    else:
        adherence_score = 0.0
        readability_score = evaluate_flesch(message)

    return {
        'adherence': adherence_score,
        'readability': readability_score,
        'accuracy': None,
        'overall': None
    }

def main(database_path: str, reset: bool, fill_overall: bool):
    conn = sqlite3.connect(database_path)

    if reset:
        delete_evaluated_table(conn)
        conn.close()
        return

    create_evaluated_table(conn)

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM commits')
    human_commits = cursor.fetchall()

    cursor.execute('SELECT * FROM ai_commits_one_shot')
    ai_commits = cursor.fetchall()

    total_commits = len(human_commits)

    for commit in tqdm(human_commits, total=total_commits, desc="Evaluating human commits", unit="commit"):
        human_scores = evaluate_commit(commit)
        ai_commit = [row for row in ai_commits if row[0] == commit[0]]
        if ai_commit:
            ai_scores = evaluate_commit(ai_commit[0])
        else:
            ai_scores = {'adherence': None, 'readability': None, 'accuracy': None}

        insert_evaluated(conn, commit[0], human_scores, ai_scores)

    if fill_overall:
        cursor.execute('SELECT * FROM evaluated')
        evaluated_commits = cursor.fetchall()
        for commit in tqdm(evaluated_commits, total=len(evaluated_commits), desc="Filling overall scores", unit="commit"):
            hash, human_adherence, human_readability, human_accuracy, _, ai_adherence, ai_readability, ai_accuracy, _ = commit
            human_overall = calculate_overall_score(human_adherence, human_readability, human_accuracy)
            ai_overall = calculate_overall_score(ai_adherence, ai_readability, ai_accuracy)
            update_overall_scores(conn, hash, human_overall, ai_overall)

    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate commit messages in an SQLite database.')
    parser.add_argument('database', type=str, help='Path to the SQLite database file.')
    parser.add_argument('--reset', action='store_true', help='Delete the evaluated table and exit.')
    parser.add_argument('-o', '--overall', action='store_true', help='Fill in the overall scores for each row.')

    args = parser.parse_args()
    
    main(args.database, args.reset, args.overall)
