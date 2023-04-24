import sqlite3
import random
import sys
import argparse

# Parse the command line arguments
parser = argparse.ArgumentParser(description='Select a random subset of commits from a SQLite database table.')
parser.add_argument('database', help='the name of the SQLite database file')
parser.add_argument('num_commits', type=int, help='the number of random commits to select')
parser.add_argument('-r', '--reverse', action='store_true', help='reverse the changes made by this script')
args = parser.parse_args()

# Connect to the database
conn = sqlite3.connect(args.database)
c = conn.cursor()

if args.reverse:
    # Check if the adaptation was done
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='all_commits'")
    if c.fetchone() is None:
        print("Error: the 'all_commits' table doesn't exist.")
        conn.close()
        sys.exit()

    # Delete the 'commits' table and rename 'all_commits' back to 'commits'
    print("Deleting the 'commits' table...")
    c.execute("DROP TABLE commits")
    print("Renaming the 'all_commits' table back to 'commits'...")
    c.execute("ALTER TABLE all_commits RENAME TO commits")

else:
    # Check if the adaptation was already done
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='all_commits'")
    if c.fetchone() is not None:
        print("Error: the 'all_commits' table already exists.")
        conn.close()
        sys.exit()

    # Rename the 'commits' table to 'all_commits'
    print("Renaming the 'commits' table to 'all_commits'...")
    c.execute("ALTER TABLE commits RENAME TO all_commits")

    # Create a new 'commits' table
    print("Creating a new 'commits' table...")
    c.execute("CREATE TABLE commits(hash TEXT PRIMARY KEY, message TEXT, diff TEXT)")

    # Get random rows from 'all_commits' table
    print(f"Selecting {args.num_commits} random commits from the 'all_commits' table...")
    c.execute(f"SELECT * FROM all_commits ORDER BY RANDOM() LIMIT {args.num_commits}")
    rows = c.fetchall()

    # Insert the selected rows into the new 'commits' table
    print("Inserting the selected rows into the new 'commits' table...")
    c.executemany("INSERT INTO commits(hash, message, diff) VALUES (?, ?, ?)", rows)

# Commit the changes and close the connection
print("Committing the changes and closing the connection...")
conn.commit()
conn.close()

print("Done!")
