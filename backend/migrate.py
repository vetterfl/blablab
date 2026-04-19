#!/usr/bin/env python3
"""Migrate users.json and presets.yaml into SQLite. Safe to re-run (idempotent)."""
import json
from pathlib import Path
from database import engine, Base, SessionLocal
from models import User, Preset
from config import load_presets

USERS_FILE = Path(__file__).parent / "users.json"


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Migrate users
        users_data = json.loads(USERS_FILE.read_text()) if USERS_FILE.exists() else []
        presets_data = load_presets()

        for u in users_data:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if existing:
                print(f"  User '{u['username']}' already exists, skipping")
                continue
            user = User(username=u["username"], hashed_password=u["hashed_password"])
            db.add(user)
            db.flush()  # get user.id

            # Seed presets for this user
            for i, p in enumerate(presets_data):
                preset = Preset(
                    user_id=user.id, slug=p["id"], label=p["label"],
                    prompt=p["prompt"], position=i,
                )
                db.add(preset)
            print(f"  Migrated user '{u['username']}' with {len(presets_data)} presets")

        db.commit()
        print("Migration complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
