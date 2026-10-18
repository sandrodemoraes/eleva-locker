#!/usr/bin/env python3
"""Inicializa banco PostgreSQL via criar_banco()."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://eleva:eleva@localhost:5432/elevalocker"

from database import criar_banco

if __name__ == "__main__":
    criar_banco()
    print("PostgreSQL inicializado.")
