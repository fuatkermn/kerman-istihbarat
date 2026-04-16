#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from datetime import datetime

from core.matrix_bg import MatrixBackground
from core.database import Database
from core.tool_manager import ToolManager

class KermanMainUI:
    """Gelişmiş ana kullanıcı arayüzü."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("KERMAN İSTİHBARAT v1.0")
        self.root.geometry("1400x900")
        self.root.configure(bg='black')
        
        # Bileşenler
        self.db = Database()
        self.tool_manager = ToolManager()
        self.output_queue = queue.Queue()
        self.current_process = None
        
        # Hedef değişkenleri
        self.target_vars = {
            "target": tk.StringVar(),
            "interface": tk.StringVar(value="wlan0"),
            "bssid": tk.StringVar(),
            "wordlist": tk.StringVar(value="/usr/share/wordlists/rockyou.txt"),
            "domain": tk.StringVar(),
            "user": tk.StringVar(),
            "port": tk.StringVar(value="80"),
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Ana arayüzü oluşturur."""
        
        # Canvas (Matrix efekti için)
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Matrix efektini başlat
        self.matrix = MatrixBackground(self.canvas, 1400, 900)
        self.matrix.draw()
        
        # Ana container (şeffaf görünüm için)
        main_container = tk.Frame(self.root, bg='#0a0a0a')
        main_container.place(relx=0.5, rely=0.5, anchor="center", 
                             width=1350, height=850)
        
        # Üst başlık
        self.create_header(main_container)
        
        # Sol panel (Kategoriler ve araçlar)
        self.create_left_panel(main_container)
        
        # Sağ panel (Hedef ve terminal)
        self.create_right_panel(main_container)
        
        # Alt durum çubuğu
        self.create_status_bar(main_container)
        
        # Terminal güncelleme döngüsü
        self.update_terminal()
    
    def create_header(self, parent):
        header = tk.Frame(parent, bg='#0a0a0a', height=50)
        header.pack(fill="x", padx=10, pady=5)
        
        title = tk.Label(header, text="⚡ KERMAN İSTİHBARAT FRAMEWORK ⚡",
                         fg="#00ff00", bg="#0a0a0a", font=("Courier", 16, "bold"))
        title.pack(side="left", padx=10)
        
        # Monitör mod göstergesi
        self.monitor_label = tk.Label(header, text="📡 Monitör: KAPALI",
                                      fg="red", bg="#0a0a0a", font=("Courier", 10))
        self.monitor_label.pack(side="right", padx=10)
    
    def create_left_panel(self, parent):
        left_frame = tk.Frame(parent, bg='#0a0a0a', width=350)
        left_frame.pack(side="left", fill="both", expand=False, padx=5, pady=5)
        left_frame.pack_propagate(False)
        
        # Sekmeler (Kategoriler)
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Stil
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#0a0a0a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#1a1a1a', foreground='#00ff00', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#003300')])
        
        # Kategorileri yükle
        self.tool_listboxes = {}
        categories = ["WiFi", "OSINT", "Web", "Exploit", "AD", "Cloud"]
        
        for cat in categories:
            frame = tk.Frame(self.notebook, bg='#0a0a0a')
            self.notebook.add(frame, text=cat)
            
            list_frame = tk.Frame(frame, bg='#0a0a0a')
            list_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side="right", fill="y")
            
            listbox = tk.Listbox(list_frame, bg='#111', fg='#00ff00',
                                 font=("Courier", 10), selectbackground='#003300',
                                 yscrollcommand=scrollbar.set)
            listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=listbox.yview)
            
            self.tool_listboxes[cat] = listbox
            
            # Araçları listeye ekle
            tools = self.tool_manager.get_tools_by_category(cat)
            for tool in tools:
                listbox.insert(tk.END, f"{tool.tool_id}. {tool.name}")
            
            listbox.bind("<Double-Button-1>", lambda e, c=cat: self.run_selected_tool(c))
        
        # Araç numarası girişi
        cmd_frame = tk.Frame(left_frame, bg='#0a0a0a')
        cmd_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(cmd_frame, text="Araç No:", fg="#00ff00", bg="#0a0a0a").pack(side="left")
        self.tool_entry = tk.Entry(cmd_frame, bg='#111', fg='#00ff00', width=5,
                                   insertbackground='#00ff00')
        self.tool_entry.pack(side="left", padx=5)
        self.tool_entry.bind("<Return>", lambda e: self.run_selected_tool())
        
        tk.Button(cmd_frame, text="ÇALIŞTIR", command=self.run_selected_tool,
                  bg="#003300", fg="#00ff00", font=("Courier", 10, "bold")).pack(side="right")
    
    def create_right_panel(self, parent):
        right_frame = tk.Frame(parent, bg='#0a0a0a')
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Hedef paneli (Kırmızı kutu)
        target_frame = tk.LabelFrame(right_frame, text="🎯 HEDEF PANELİ",
                                     fg="red", bg="#0a0a0a", font=("Courier", 12, "bold"),
                                     relief="solid", bd=2)
        target_frame.pack(fill="x", padx=5, pady=5)
        
        fields = [
            ("Hedef IP/URL:", "target"),
            ("Arayüz:", "interface"),
            ("BSSID:", "bssid"),
            ("Domain:", "domain"),
            ("Kullanıcı:", "user"),
            ("Port:", "port"),
        ]
        
        for i, (label, var_name) in enumerate(fields):
            f = tk.Frame(target_frame, bg='#0a0a0a')
            f.grid(row=i//2, column=i%2, padx=5, pady=2, sticky="ew")
            
            tk.Label(f, text=label, fg="red", bg="#0a0a0a", width=12, anchor="w").pack(side="left")
            entry = tk.Entry(f, textvariable=self.target_vars[var_name],
                            bg='#1a0000', fg='#ff6666', insertbackground='red', width=25)
            entry.pack(side="left", fill="x", expand=True)
        
        # Wordlist alanı
        wl_frame = tk.Frame(target_frame, bg='#0a0a0a')
        wl_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        tk.Label(wl_frame, text="Wordlist:", fg="red", bg="#0a0a0a", width=12, anchor="w").pack(side="left")
        tk.Entry(wl_frame, textvariable=self.target_vars["wordlist"],
                bg='#1a0000', fg='#ff6666', insertbackground='red', width=50).pack(side="left", fill="x", expand=True)
        
        target_frame.grid_columnconfigure(0, weight=1)
        target_frame.grid_columnconfigure(1, weight=1)
        
        # Terminal çıktısı
        term_frame = tk.LabelFrame(right_frame, text="📟 TERMİNAL ÇIKTISI",
                                   fg="#00ff00", bg="#0a0a0a", font=("Courier", 12, "bold"))
        term_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.terminal = scrolledtext.ScrolledText(term_frame, bg='#0a0a0a', fg='#00ff00',
                                                  font=("Courier", 10), insertbackground='#00ff00')
        self.terminal.pack(fill="both", expand=True)
        
        self.terminal.insert(tk.END, "╔" + "═" * 78 + "╗\n")
        self.terminal.insert(tk.END, "║" + " KERMAN İSTİHBARAT TERMİNAL ".center(78) + "║\n")
        self.terminal.insert(tk.END, "╚" + "═" * 78 + "╝\n\n")
        self.terminal.insert(tk.END, "[*] Sistem hazır. Araç numarası girin veya listeden seçin.\n\n")
        self.terminal.see(tk.END)
    
    def create_status_bar(self, parent):
        status = tk.Frame(parent, bg='#0a0a0a', height=25)
        status.pack(fill="x", side="bottom", padx=10, pady=5)
        
        self.status_label = tk.Label(status, text="Hazır", fg="#00ff00", bg="#0a0a0a",
                                     font=("Courier", 9), anchor="w")
        self.status_label.pack(side="left")
        
        time_label = tk.Label(status, text=datetime.now().strftime("%H:%M:%S"),
                              fg="#666", bg="#0a0a0a", font=("Courier", 9))
        time_label.pack(side="right")
    
    def run_selected_tool(self, category=None):
        """Seçili aracı çalıştırır."""
        try:
            tool_id = int(self.tool_entry.get())
        except:
            if category:
                selection = self.tool_listboxes[category].curselection()
                if selection:
                    tool_str = self.tool_listboxes[category].get(selection[0])
                    tool_id = int(tool_str.split(".")[0])
                else:
                    return
            else:
                return
        
        tool = self.tool_manager.get_tool(tool_id)
        if not tool:
            messagebox.showerror("Hata", f"Araç bulunamadı: {tool_id}")
            return
        
        # Parametreleri hazırla
        params = {k: v.get() for k, v in self.target_vars.items()}
        
        self.terminal.insert(tk.END, f"\n[{datetime.now().strftime('%H:%M:%S')}] Çalıştırılıyor: {tool.name}\n")
        self.terminal.insert(tk.END, f"[CMD] {tool.command}\n")
        self.terminal.insert(tk.END, "-" * 80 + "\n")
        self.terminal.see(tk.END)
        
        self.status_label.config(text=f"Çalışıyor: {tool.name}")
        
        # Veritabanına kaydet
        self.db.add_operation(tool.name, tool.command, params.get("target", ""))
        
        # Arka planda çalıştır
        threading.Thread(target=self._run_tool_thread, args=(tool_id, params), daemon=True).start()
    
    def _run_tool_thread(self, tool_id, params):
        """Aracı arka planda çalıştırır."""
        result = self.tool_manager.run_tool(tool_id, params)
        
        if "error" in result:
            self.output_queue.put(f"\n[HATA] {result['error']}\n")
        else:
            self.output_queue.put(result.get("stdout", ""))
            if result.get("stderr"):
                self.output_queue.put(f"\n[STDERR]\n{result['stderr']}\n")
            self.output_queue.put(f"\n[İŞLEM TAMAMLANDI] Çıkış kodu: {result['return_code']}\n")
        
        self.output_queue.put("\n[>] Hazır. Yeni komut bekleniyor...\n")
    
    def update_terminal(self):
        """Terminal çıktısını günceller."""
        try:
            while True:
                line = self.output_queue.get_nowait()
                self.terminal.insert(tk.END, line)
                self.terminal.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.update_terminal)
    
    def stop_matrix(self):
        """Matrix efektini durdurur."""
        if hasattr(self, 'matrix'):
            self.matrix.stop()
