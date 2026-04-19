#!/usr/bin/env python3
"""Manage users in the database.

Usage:
  python add_user.py add <username> <password> [--admin]
  python add_user.py delete <username>
"""
import sys

from database import engine, Base, SessionLocal
from services.users import get_user_by_username, create_user, delete_user
from auth import hash_password


def cmd_add(args):
    is_admin = "--admin" in args
    args = [a for a in args if a != "--admin"]
    if len(args) != 2:
        print("Usage: python add_user.py add <username> <password> [--admin]")
        sys.exit(1)
    username, password = args
    db = SessionLocal()
    try:
        if get_user_by_username(db, username):
            print(f"Error: user '{username}' already exists")
            sys.exit(1)
        create_user(db, username, hash_password(password), is_admin=is_admin)
        role = "admin" if is_admin else "user"
        print(f"User '{username}' added ({role}).")
    finally:
        db.close()


def cmd_delete(args):
    if len(args) != 1:
        print("Usage: python add_user.py delete <username>")
        sys.exit(1)
    username = args[0]
    db = SessionLocal()
    try:
        user = get_user_by_username(db, username)
        if not user:
            print(f"Error: user '{username}' not found")
            sys.exit(1)
        delete_user(db, user.id)
        print(f"User '{username}' deleted.")
    finally:
        db.close()


COMMANDS = {"add": cmd_add, "delete": cmd_delete}


def main():
    Base.metadata.create_all(bind=engine)
    args = sys.argv[1:]
    if not args or args[0] not in COMMANDS:
        print("Usage:")
        print("  python add_user.py add <username> <password> [--admin]")
        print("  python add_user.py delete <username>")
        sys.exit(1)
    COMMANDS[args[0]](args[1:])


if __name__ == "__main__":
    main()
