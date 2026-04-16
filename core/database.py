#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class Database:
    """SQLite veritabanı yönetimi."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            home = Path.home()
            db_dir = home / ".kerman"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "data.db"
        
        self.db_path = Path(db_path)
        self.init_database()
    
    def _connect(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Tabloları oluşturur."""
        conn = self._connect()
        c = conn.cursor()
        
        # Hedefler tablosu
        c.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ip TEXT,
                mac TEXT,
                domain TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # İşlemler tablosu
        c.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                command TEXT NOT NULL,
                target TEXT,
                output TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bulgular tablosu
        c.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                title TEXT NOT NULL,
                severity TEXT,
                description TEXT,
                cve TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(target_id) REFERENCES targets(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"[✓] Veritabanı hazır: {self.db_path}")
    
    def add_target(self, name: str, **kwargs) -> int:
        """Yeni hedef ekler."""
        conn = self._connect()
        c = conn.cursor()
        
        fields = ['name']
        values = [name]
        for k, v in kwargs.items():
            if v:
                fields.append(k)
                values.append(v)
        
        query = f"INSERT INTO targets ({','.join(fields)}) VALUES ({','.join(['?']*len(fields))})"
        c.execute(query, values)
        conn.commit()
        target_id = c.lastrowid
        conn.close()
        return target_id
    
    def add_operation(self, tool_name: str, command: str, target: str = "", 
                      output: str = "", status: str = "RUNNING") -> int:
        """İşlem kaydı ekler."""
        conn = self._connect()
        c = conn.cursor()
        c.execute('''
            INSERT INTO operations (tool_name, command, target, output, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (tool_name, command, target, output, status))
        conn.commit()
        op_id = c.lastrowid
        conn.close()
        return op_id
    
    def get_targets(self, limit: int = 50) -> List[Dict]:
        """Hedefleri listeler."""
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT * FROM targets ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_operations(self, limit: int = 50) -> List[Dict]:
        """İşlemleri listeler."""
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT * FROM operations ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
