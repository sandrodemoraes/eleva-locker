#!/usr/bin/env python3
"""Restaura site_id de armários que sumiram da lista após editar."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.base_repository import BaseRepository

with BaseRepository.get_connection() as conn:
    n = conn.execute("""
        UPDATE armarios SET site_id = 1 WHERE site_id IS NULL
    """).rowcount
    conn.commit()

print(f"Armários corrigidos: {n}")
