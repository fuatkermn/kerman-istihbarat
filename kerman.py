#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KERMAN İSTİHBARAT FRAMEWORK
Sürüm: 1.0.0
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess

# Root kontrolü
if os.geteuid() != 0:
    print("HATA: Bu uygulama root yetkileri ile çalıştırılmalıdır!")
    print("Lütfen: sudo python3 kerman.py")
    sys.exit(1)

# Core modülleri import et
from core.database import Database
from core.tool_manager import ToolManager
from core.helpers import SystemInfo

class KermanLogin:
    """Giriş ekranı."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KERMAN İSTİHBARAT - GİRİŞ")
        self.root.geometry("500x300")
        self.root.configure(bg='black')
        self.root.resizable(False, False)
        
        self.password = "kerman"
        self.setup_ui()
    
    def setup_ui(self):
        # Başlık
        title = tk.Label(self.root, text="⚡ KERMAN İSTİHBARAT ⚡",
                         fg="#00ff00", bg="black", font=("Courier", 20, "bold"))
        title.pack(pady=30)
        
        # Şifre alanı
        pwd_frame = tk.Frame(self.root, bg='black')
        pwd_frame.pack(pady=20)
        
        tk.Label(pwd_frame, text="Şifre:", fg="#00ff00", bg="black",
                 font=("Courier", 14)).pack(side=tk.LEFT, padx=10)
        
        self.pwd_entry = tk.Entry(pwd_frame, show="•", bg="#0a0a0a", fg="#00ff00",
                                  font=("Courier", 14), width=20, insertbackground="#00ff00")
        self.pwd_entry.pack(side=tk.LEFT)
        self.pwd_entry.bind("<Return>", lambda e: self.check_password())
        self.pwd_entry.focus()
        
        # Giriş butonu
        btn = tk.Button(self.root, text="GİRİŞ", command=self.check_password,
                        bg="#003300", fg="#00ff00", font=("Courier", 12, "bold"),
                        activebackground="#005500", activeforeground="#00ff00",
                        width=15, height=2)
        btn.pack(pady=20)
        
        # Versiyon
        version = tk.Label(self.root, text="v1.0.0 | Kali Linux", fg="#666666", bg="black",
                           font=("Courier", 8))
        version.pack(side=tk.BOTTOM, pady=5)
    
    def check_password(self):
        if self.pwd_entry.get() == self.password:
            self.root.destroy()
            app = KermanMain()
            app.run()
        else:
            messagebox.showerror("Hata", "Yanlış şifre!")
            self.pwd_entry.delete(0, tk.END)
    
    def run(self):
        self.root.mainloop()

class KermanMain:
    """Ana uygulama penceresi."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KERMAN İSTİHBARAT")
        self.root.geometry("1200x700")
        self.root.configure(bg='black')
        
        self.db = Database()
        self.tool_manager = ToolManager()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Ana çerçeve
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Hoşgeldin mesajı
        welcome = tk.Label(main_frame, 
                          text="KERMAN İSTİHBARAT FRAMEWORK\n\n"
                               "Bu proje geliştirme aşamasındadır.\n"
                               "Sonraki parçalarla genişletilecektir.",
                          fg="#00ff00", bg="black", font=("Courier", 14),
                          justify=tk.CENTER)
        welcome.pack(expand=True)
        
        # Sistem bilgisi
        sys_info = SystemInfo.get_summary()
        info_label = tk.Label(main_frame, text=sys_info, fg="#666666", bg="black",
                              font=("Courier", 10), justify=tk.LEFT)
        info_label.pack(side=tk.BOTTOM, pady=10)
        
        # Çıkış butonu
        btn = tk.Button(main_frame, text="ÇIKIŞ", command=self.root.quit,
                        bg="#330000", fg="red", font=("Courier", 10),
                        width=10)
        btn.pack(side=tk.BOTTOM, pady=10)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    login = KermanLogin()
    login.run()
