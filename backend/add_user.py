#!/usr/bin/env python3
"""Add a user to the database.

Usage: python add_user.py <username> <password>
"""
import sys

from database import engine, Base, SessionLocal
from services.users import get_user_by_username, create_user
from auth import hash_password


def main():
    if len(sys.argv) != 3:
        print("Usage: python add_user.py <username> <password>")
        sys.exit(1)

    username, password = sys.argv[1], sys.argv[2]

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if get_user_by_username(db, username):
            print(f"Error: user '{username}' already exists")
            sys.exit(1)

        create_user(db, username, hash_password(password))
        print(f"User '{username}' added.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
