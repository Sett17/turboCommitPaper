import sqlite3
import os
import sys
from git import Repo
from git import Git
from tqdm import tqdm

def is_bot_commit(commit):
    author_name = commit.author.name.lower()
    message = commit.message.lower()
    return (
        "bot" in author_name
        or "snyk" in author_name
        or "merge" in message
    )

def clone_repository(repo_url, local_path):
    if not os.path.exists(local_path):
        Repo.clone_from(repo_url, local_path)
    repo = Repo(local_path)
    return repo

def init_database(database_file):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS commits (hash TEXT, message TEXT, diff TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bot_commits (hash TEXT, message TEXT)''')
    conn.commit()
    return conn

def save_commit_data(conn, commit_hash, message, diff, is_bot=False):
    cursor = conn.cursor()
    if is_bot:
        cursor.execute("INSERT INTO bot_commits (hash, message) VALUES (?, ?)", (commit_hash, message))
    else:
        cursor.execute("INSERT INTO commits (hash, message, diff) VALUES (?, ?, ?)", (commit_hash, message, diff))
    conn.commit()

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <repository_url>")
        sys.exit(1)

    repo_url = sys.argv[1]
    repo_name = repo_url.split("/")[-1].split(".")[0]
    local_path = repo_name
    database_file = f"{repo_name}.db"

    repo = clone_repository(repo_url, local_path)
    conn = init_database(database_file)
    git = Git(local_path)

    commit_count = len(list(repo.iter_commits()))
    progress_bar = tqdm(total=commit_count, desc="Processing commits", ncols=100)

    for commit in repo.iter_commits():
        commit_hash = commit.hexsha
        message = commit.message.strip()
        is_bot = is_bot_commit(commit)
        # diff = git.diff(commit.parents[0].hexsha, commit.hexsha) if commit.parents else git.diff(commit.hexsha)
        diff = (git.diff(commit.parents[0].hexsha, commit.hexsha) if commit.parents else git.diff(commit.hexsha)).encode('utf-8', 'replace').decode('utf-8')
        save_commit_data(conn, commit_hash, message, diff, is_bot)
        progress_bar.update(1)

    progress_bar.close()
    conn.close()

if __name__ == "__main__":
    main()
