import os
import os.path
import sys
import sqlite3
from typing import List, Tuple
import subprocess
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import TerminalFormatter
import click

def create_ai_commits_table(database_path: str) -> None:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_commits (
            hash TEXT PRIMARY KEY,
            content TEXT
        )
    """)
    connection.commit()
    connection.close()

def display_diff(diff: str) -> None:
    highlighted_diff = highlight(diff, DiffLexer(), TerminalFormatter())
    pager = subprocess.Popen(["less", "-R"], stdin=subprocess.PIPE, universal_newlines=True)
    pager.communicate(highlighted_diff)
    pager.wait()

def get_commits(database_path: str, n: int) -> List[Tuple[str, str, str]]:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT hash, message, diff
        FROM commits
        WHERE hash NOT IN (SELECT hash FROM ai_commits)
        ORDER BY RANDOM()
        LIMIT ?
    """, (n,))
    commits = cursor.fetchall()
    connection.close()
    return commits

def ai_commit_exists(database_path: str, hash: str) -> bool:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM ai_commits WHERE hash = ?", (hash,))
    count = cursor.fetchone()[0]
    connection.close()
    return count > 0

def save_to_file(filename: str, content: str) -> None:
    with open(filename, "w") as file:
        file.write(content)

def read_file(filename: str) -> str:
    with open(filename, "r") as file:
        content = file.read()
    return content

def delete_files(filepaths: List[str]) -> None:
    for filepath in filepaths:
        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            print(f"File '{filepath}' not found. Skipping deletion.")


def call_turbocommit(extra_arg: str) -> int:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    executable_path = os.path.join(script_dir, "adapted_turbocommit")
    return os.system(f"{executable_path} {extra_arg}")

def insert_ai_commit(database_path: str, hash: str, content: str) -> None:
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO ai_commits (hash, content) VALUES (?, ?)", (hash, content))
    connection.commit()
    connection.close()

def main(database_path: str, n: int) -> None:
    create_ai_commits_table(database_path)
    commits = get_commits(database_path, n)

    for hash, message, diff in commits:
        if ai_commit_exists(database_path, hash):
            print(f"AI commit already exists for hash {hash}")
            continue

        separator_line = "-" * 80
        print(separator_line)
        print(message)
        print(separator_line)

        input("Press Enter to view the diff...")
        display_diff(diff)

        while True:
            extra_arg = input("Enter an extra string for adapted_turbocommit: ")

            print("Running adapted_turbocommit...")
            save_to_file("diff.txt", diff)
            exit_code = call_turbocommit(extra_arg)

            if exit_code != 0:
                print(f"adapted_turbocommit exited with non-zero code: {exit_code}")
                retry = click.prompt("Do you want to try again?", type=click.Choice(['y', 'n'], case_sensitive=False), default='y', show_default=True)

                if retry == 'y':
                    continue
                else:
                    break
            else:
                print("adapted_turbocommit finished. Saving AI commit...")
                output = read_file("output.txt")
                insert_ai_commit(database_path, hash, output)
                break

        delete_files(["diff.txt", "output.txt"])
        print(f"AI commit saved for hash {hash}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <database_path> <number_of_rows>")
        sys.exit(1)

    database_path = sys.argv[1]
    n = int(sys.argv[2])

    main(database_path, n)
