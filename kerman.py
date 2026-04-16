#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KERMAN İSTİHBARAT ÇERÇEVESİ
Sürüm: 2.0.0 FULL
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys

if os.geteuid() != 0:
    print("HATA: Bu uygulama root yetkileri ile çalıştırılmalıdır!")
    print("Lütfen: sudo python3 kerman.py")
    sys.exit(1)

class KermanLogin:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KERMAN İSTİHBARAT - GİRİŞ")
        self.root.geometry("500x300")
        self.root.configure(bg='black')
        self.root.resizable(False, False)
        self.password = "kerman"
        self.setup_ui()
    
    def setup_ui(self):
        title = tk.Label(self.root, text="⚡ KERMAN İSTİHBARAT ⚡", fg="#00ff00", bg="black", font=("Courier", 20, "bold"))
        title.pack(pady=30)
        pwd_frame = tk.Frame(self.root, bg='black')
        pwd_frame.pack(pady=20)
        tk.Label(pwd_frame, text="Parola:", fg="#00ff00", bg="black", font=("Courier", 14)).pack(side=tk.LEFT, padx=10)
        self.pwd_entry = tk.Entry(pwd_frame, show="•", bg="#0a0a0a", fg="#00ff00", font=("Courier", 14), width=20, insertbackground="#00ff00")
        self.pwd_entry.pack(side=tk.LEFT)
        self.pwd_entry.bind("<Return>", lambda e: self.check_password())
        self.pwd_entry.focus()
        btn = tk.Button(self.root, text="GİRİŞ", command=self.check_password, bg="#003300", fg="#00ff00", font=("Courier", 12, "bold"), activebackground="#005500", activeforeground="#00ff00", width=15, height=2)
        btn.pack(pady=20)
        version = tk.Label(self.root, text="v2.0.0 FULL | Kali Linux", fg="#666666", bg="black", font=("Courier", 8))
        version.pack(side=tk.BOTTOM, pady=5)
    
    def check_password(self):
        if self.pwd_entry.get() == self.password:
            self.root.destroy()
            from core.ui import KermanMainUI
            root = tk.Tk()
            app = KermanMainUI(root)
            def on_closing():
                app.stop_matrix()
                root.destroy()
            root.protocol("WM_DELETE_WINDOW", on_closing)
            root.mainloop()
        else:
            messagebox.showerror("Hata", "Yanlış parola!")
            self.pwd_entry.delete(0, tk.END)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    login = KermanLogin()
    login.run()
