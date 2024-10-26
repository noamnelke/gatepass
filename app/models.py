import logging
import os
import sqlite3
from config import Config


def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_user(credential_id, public_key, building, apartment, name):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (credential_id, public_key, building, apartment, name) VALUES (?, ?, ?, ?, ?)",
        (credential_id, public_key, building, apartment, name),
    )
    conn.commit()
    user_id = c.lastrowid
    if user_id == 1:
        c.execute("UPDATE users SET admin=1 WHERE id=1")
        conn.commit()
    conn.close()
    return user_id


def get_user(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT building, apartment, name, validated, admin FROM users WHERE id=?",
        (user_id,),
    )
    user = c.fetchone()
    conn.close()
    return {
        "id": user_id,
        "building": user["building"],
        "apartment": user["apartment"],
        "name": user["name"],
        "validated": user["validated"],
        "admin": user["admin"],
    }


def get_user_by_credential_id(credential_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, public_key, validated, admin FROM users WHERE credential_id=?",
        (credential_id,),
    )
    user = c.fetchone()
    conn.close()
    return {
        "id": user["id"],
        "public_key": user["public_key"],
        "validated": user["validated"],
        "admin": user["admin"],
    }


def update_user(user):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET building=?, apartment=?, name=?, validated=?, admin=? WHERE id=?",
        (
            user["building"],
            user["apartment"],
            user["name"],
            "validated" in user,
            "admin" in user,
            user["id"],
        ),
    )
    conn.commit()
    conn.close()


def init_db():
    if not os.path.exists(Config.DATABASE):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credential_id TEXT UNIQUE NOT NULL,
                public_key TEXT NOT NULL,
                building INTEGER NOT NULL,
                apartment TEXT NOT NULL,
                name TEXT,
                validated INTEGER NOT NULL DEFAULT 1,
                admin INTEGER NOT NULL DEFAULT 0
            )
        """
        )
        conn.commit()
        conn.close()
        logging.info("Initialized database.")


init_db()
