import sqlite3
import os
import random
import subprocess
import sys
import psutil
import random
import click

def get_commits(db_path, num_commits):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT commits.hash, commits.message, ai_commits_one_shot.content, commits.diff
        FROM commits
        JOIN ai_commits_one_shot ON commits.hash = ai_commits_one_shot.hash
        LEFT JOIN evaluated ON commits.hash = evaluated.hash
        WHERE evaluated.hash IS NULL OR evaluated.human_accuracy IS NULL OR evaluated.ai_accuracy IS NULL
        ORDER BY RANDOM()
        LIMIT ?
        """, (num_commits,))

        results = cur.fetchall()

    return results

def get_ai_commit(db_path, commit_hash):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM ai_commits_one_shot WHERE hash=?", (commit_hash,))
        return cursor.fetchone()[0]

def update_evaluated(db_path, commit_hash, human_accuracy, ai_accuracy):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE evaluated
            SET human_accuracy = ?, ai_accuracy = ?
            WHERE hash = ?
        """, (human_accuracy, ai_accuracy, commit_hash))
        conn.commit()

def open_diff_in_editor(diff):
    with open("temp_diff.diff", "w") as f:
        f.write(diff)

RUBRIC = """1 = 1.0: The commit message accurately and completely describes the changes made in the code.
2 = 0.8: The commit message accurately describes most of the changes, but misses some minor details.
3 = 0.6: The commit message describes some of the changes accurately, but significant portions are missing or unclear.
4 = 0.4: The commit message is only somewhat accurate, with numerous missing or incorrect details.
5 = 0.2: The commit message barely describes the changes made, with little to no accurate information.
6 = 0.0: The commit message does not accurately describe the changes at all."""

def evaluate_messages(human_message, ai_message):
    print("\n\033[0;31m" + "-" * 35 + "READ  DIFF"  + "-" * 35 + "\033[0;0m")

    messages = [("Human", human_message), ("AI", ai_message)]
    random.shuffle(messages)
    evaluations = {}
    score_options = [1.0, 0.8, 0.6, 0.4, 0.2, 0.0]

    for label, message in messages:
        print("=" * 40 + "\n" + message + "\n" + "=" * 40 + "\n")
        
        print("Select the score by entering the index (1-6):")
        # for idx, option in enumerate(score_options, start=1):
        #     print(f"{idx}. {option}")
        print(RUBRIC)

        selected_index = click.prompt("Enter the index of the score", type=click.IntRange(0, 6)) - 1
        if selected_index == -1:
            print("Skipping...")
            return None
        score = score_options[selected_index]
        evaluations[label.lower()] = score

    return evaluations

def main(db_path, num_commits):
    commits = get_commits(db_path, num_commits)

    for commit in commits:
        commit_hash, human_message, ai_message, diff = commit

        open_diff_in_editor(diff)

        scores = evaluate_messages(human_message, ai_message)
        if scores is None:
            continue
        update_evaluated(db_path, commit_hash, scores["human"], scores["ai"])

        os.remove("temp_diff.diff")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <path_to_database> <number_of_commits>")
        sys.exit(1)

    db_path = sys.argv[1]
    num_commits = int(sys.argv[2])

    main(db_path, num_commits)
