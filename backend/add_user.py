#!/usr/bin/env python3
"""Add a user to users.json.

Usage: python add_user.py <username> <password>
"""
import json
import sys
from pathlib import Path

from auth import hash_password

USERS_FILE = Path(__file__).parent / "users.json"


def main():
    if len(sys.argv) != 3:
        print("Usage: python add_user.py <username> <password>")
        sys.exit(1)

    username, password = sys.argv[1], sys.argv[2]
    users = json.loads(USERS_FILE.read_text()) if USERS_FILE.exists() else []

    if any(u["username"] == username for u in users):
        print(f"Error: user '{username}' already exists")
        sys.exit(1)

    users.append({"username": username, "hashed_password": hash_password(password)})
    USERS_FILE.write_text(json.dumps(users, indent=2))
    print(f"User '{username}' added.")


if __name__ == "__main__":
    main()
