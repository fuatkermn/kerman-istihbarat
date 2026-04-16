#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
import subprocess
import re
from datetime import datetime

from core.matrix_bg import MatrixBackground
from core.database import Database
from core.tool_manager import ToolManager
from core.report_generator import ReportGenerator
from core.ai_module import AIModule
from core.voice_module import VoiceModule

class KermanMainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KERMAN İSTİHBARAT v2.0 FULL")
        self.root.geometry("1400x900")
        self.root.configure(bg='black')
        
        self.db = Database()
        self.tool_manager = ToolManager()
        self.report_gen = ReportGenerator(self.db)
        self.ai_module = AIModule()
        self.output_queue = queue.Queue()
        self.voice_module = VoiceModule(self.output_queue)
        
        self.monitor_mode_active = False
        self.current_interface = "wlan0"
        self.current_op_id = None
        self.current_output = ""
        
        self.target_vars = {
            "target": tk.StringVar(),
            "interface": tk.StringVar(value="wlan0"),
            "bssid": tk.StringVar(),
            "wordlist": tk.StringVar(value="/usr/share/wordlists/rockyou.txt"),
            "domain": tk.StringVar(),
            "user": tk.StringVar(),
            "port": tk.StringVar(value="80"),
            "query": tk.StringVar(),
            "contract_addr": tk.StringVar(),
            "file": tk.StringVar(),
            "image": tk.StringVar(),
            "device": tk.StringVar(),
            "docker_image": tk.StringVar(),
            "password": tk.StringVar(),
            "hash": tk.StringVar(),
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.matrix = MatrixBackground(self.canvas, 1400, 900)
        self.matrix.draw()
        
        main_container = tk.Frame(self.root, bg='#0a0a0a')
        main_container.place(relx=0.5, rely=0.5, anchor="center", width=1350, height=850)
        
        self.create_header(main_container)
        self.create_left_panel(main_container)
        self.create_right_panel(main_container)
        self.create_status_bar(main_container)
        
        self.update_terminal()
    
    def create_header(self, parent):
        header = tk.Frame(parent, bg='#0a0a0a', height=50)
        header.pack(fill="x", padx=10, pady=5)
        
        title = tk.Label(header, text="⚡ KERMAN İSTİHBARAT v2.0 FULL ⚡", fg="#00ff00", bg="#0a0a0a", font=("Courier", 16, "bold"))
        title.pack(side="left", padx=10)
        
        monitor_frame = tk.Frame(header, bg='#0a0a0a')
        monitor_frame.pack(side="right", padx=10)
        
        self.monitor_status = tk.StringVar(value="📡 İzleme Modu: KAPALI")
        self.monitor_label = tk.Label(monitor_frame, textvariable=self.monitor_status, fg="red", bg="#0a0a0a", font=("Courier", 10))
        self.monitor_label.pack(side="left", padx=5)
        
        self.monitor_btn = tk.Button(monitor_frame, text="AÇ", command=self.toggle_monitor_mode, bg="#330000", fg="red", font=("Courier", 9), width=5)
        self.monitor_btn.pack(side="left")
    
    def create_left_panel(self, parent):
        left_frame = tk.Frame(parent, bg='#0a0a0a', width=350)
        left_frame.pack(side="left", fill="both", expand=False, padx=5, pady=5)
        left_frame.pack_propagate(False)
        
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#0a0a0a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#1a1a1a', foreground='#00ff00', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#003300')])
        
        self.tool_listboxes = {}
        kategoriler = ["WiFi", "OSINT", "Web", "Exploit", "AD", "Cloud", "DarkWeb", "Blockchain", "IoT", "Forensic", "Spyware", "Scenarios"]
        
        for kat in kategoriler:
            frame = tk.Frame(self.notebook, bg='#0a0a0a')
            self.notebook.add(frame, text=kat)
            list_frame = tk.Frame(frame, bg='#0a0a0a')
            list_frame.pack(fill="both", expand=True, padx=5, pady=5)
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side="right", fill="y")
            listbox = tk.Listbox(list_frame, bg='#111', fg='#00ff00', font=("Courier", 10), selectbackground='#003300', yscrollcommand=scrollbar.set)
            listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=listbox.yview)
            self.tool_listboxes[kat] = listbox
            araclar = self.tool_manager.get_tools_by_category(kat)
            for arac in araclar:
                listbox.insert(tk.END, f"{arac.tool_id}. {arac.name}")
            listbox.bind("<Double-Button-1>", lambda e, c=kat: self.run_selected_tool(c))
        
        cmd_frame = tk.Frame(left_frame, bg='#0a0a0a')
        cmd_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(cmd_frame, text="Araç No:", fg="#00ff00", bg="#0a0a0a").pack(side="left")
        self.tool_entry = tk.Entry(cmd_frame, bg='#111', fg='#00ff00', width=5, insertbackground='#00ff00')
        self.tool_entry.pack(side="left", padx=5)
        self.tool_entry.bind("<Return>", lambda e: self.run_selected_tool())
        
        btn_frame = tk.Frame(left_frame, bg='#0a0a0a')
        btn_frame.pack(fill="x", padx=5, pady=5)
        tk.Button(btn_frame, text="▶ ÇALIŞTIR", command=self.run_selected_tool, bg="#003300", fg="#00ff00", font=("Courier", 10, "bold")).pack(side="left", padx=2)
        tk.Button(btn_frame, text="⬜ DURDUR", command=self.stop_current_tool, bg="#333300", fg="#ffff00", font=("Courier", 10)).pack(side="left", padx=2)
        tk.Button(btn_frame, text="📊 RAPOR", command=self.generate_report, bg="#000033", fg="#00ccff", font=("Courier", 10)).pack(side="left", padx=2)
        tk.Button(btn_frame, text="🤖 AI SOR", command=self.ask_ai, bg="#330033", fg="#ff00ff", font=("Courier", 10)).pack(side="left", padx=2)
        tk.Button(btn_frame, text="🎤 SESLİ", command=self.start_voice, bg="#003333", fg="#00ffff", font=("Courier", 10)).pack(side="left", padx=2)
    
    def create_right_panel(self, parent):
        right_frame = tk.Frame(parent, bg='#0a0a0a')
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        target_frame = tk.LabelFrame(right_frame, text="🎯 HEDEF BİLGİLERİ", fg="red", bg="#0a0a0a", font=("Courier", 12, "bold"), relief="solid", bd=2)
        target_frame.pack(fill="x", padx=5, pady=5)
        
        alanlar = [
            ("Hedef IP/URL:", "target", 0, 0), ("Ağ Arayüzü:", "interface", 0, 1),
            ("BSSID/MAC:", "bssid", 1, 0), ("Domain:", "domain", 1, 1),
            ("Kullanıcı Adı:", "user", 2, 0), ("Port:", "port", 2, 1),
            ("Parola:", "password", 3, 0), ("Hash:", "hash", 3, 1),
        ]
        
        for etiket, var_name, row, col in alanlar:
            f = tk.Frame(target_frame, bg='#0a0a0a')
            f.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
            tk.Label(f, text=etiket, fg="red", bg="#0a0a0a", width=12, anchor="w").pack(side="left")
            entry = tk.Entry(f, textvariable=self.target_vars[var_name], bg='#1a0000', fg='#ff6666', insertbackground='red', width=25)
            entry.pack(side="left", fill="x", expand=True)
        
        wl_frame = tk.Frame(target_frame, bg='#0a0a0a')
        wl_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        tk.Label(wl_frame, text="Parola Listesi:", fg="red", bg="#0a0a0a", width=12, anchor="w").pack(side="left")
        tk.Entry(wl_frame, textvariable=self.target_vars["wordlist"], bg='#1a0000', fg='#ff6666', insertbackground='red', width=50).pack(side="left", fill="x", expand=True)
        tk.Button(wl_frame, text="📁", command=self.browse_wordlist, bg="#330000", fg="red", width=3).pack(side="left", padx=2)
        
        target_frame.grid_columnconfigure(0, weight=1)
        target_frame.grid_columnconfigure(1, weight=1)
        
        term_frame = tk.LabelFrame(right_frame, text="📟 UÇ BİRİM ÇIKTISI", fg="#00ff00", bg="#0a0a0a", font=("Courier", 12, "bold"))
        term_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.terminal = scrolledtext.ScrolledText(term_frame, bg='#0a0a0a', fg='#00ff00', font=("Courier", 10), insertbackground='#00ff00')
        self.terminal.pack(fill="both", expand=True)
        
        self.terminal.insert(tk.END, "╔" + "═" * 78 + "╗\n")
        self.terminal.insert(tk.END, "║" + " KERMAN İSTİHBARAT v2.0 FULL ".center(78) + "║\n")
        self.terminal.insert(tk.END, "╚" + "═" * 78 + "╝\n\n")
        self.terminal.insert(tk.END, "[*] Sistem hazır. Araç numarası girin veya listeden seçin.\n")
        self.terminal.insert(tk.END, "[*] Yeni: AI Asistan, Sesli Komut, Raporlama, Monitör Mod\n\n")
        self.terminal.see(tk.END)
    
    def create_status_bar(self, parent):
        status = tk.Frame(parent, bg='#0a0a0a', height=25)
        status.pack(fill="x", side="bottom", padx=10, pady=5)
        self.status_label = tk.Label(status, text="Hazır", fg="#00ff00", bg="#0a0a0a", font=("Courier", 9), anchor="w")
        self.status_label.pack(side="left")
        self.time_label = tk.Label(status, text="", fg="#666", bg="#0a0a0a", font=("Courier", 9))
        self.time_label.pack(side="right")
        self.update_time()
    
    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)
    
    def browse_wordlist(self):
        filename = filedialog.askopenfilename(title="Parola Listesi Seç", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.target_vars["wordlist"].set(filename)
    
    def toggle_monitor_mode(self):
        if not self.monitor_mode_active:
            self.terminal.insert(tk.END, f"\n[*] {self.current_interface} monitör moda alınıyor...\n")
            self.terminal.see(tk.END)
            try:
                subprocess.run("sudo systemctl stop NetworkManager 2>/dev/null || sudo service network-manager stop 2>/dev/null", shell=True)
                subprocess.run("sudo airmon-ng check kill 2>/dev/null", shell=True)
                result = subprocess.run(f"sudo airmon-ng start {self.current_interface}", shell=True, capture_output=True, text=True)
                self.terminal.insert(tk.END, result.stdout)
                if "monitor mode enabled" in result.stdout.lower():
                    match = re.search(r'([a-zA-Z0-9]+mon)', result.stdout)
                    if match:
                        self.current_interface = match.group(1)
                self.monitor_mode_active = True
                self.monitor_status.set(f"📡 İzleme Modu: AÇIK ({self.current_interface})")
                self.monitor_label.config(fg="green")
                self.monitor_btn.config(text="KAPAT", bg="#003300", fg="green")
                self.target_vars["interface"].set(self.current_interface)
                self.terminal.insert(tk.END, f"[✓] Monitör mod aktif: {self.current_interface}\n")
            except Exception as e:
                self.terminal.insert(tk.END, f"[HATA] {str(e)}\n")
        else:
            self.terminal.insert(tk.END, f"\n[*] {self.current_interface} yönetim moduna alınıyor...\n")
            try:
                subprocess.run(f"sudo airmon-ng stop {self.current_interface}", shell=True)
                subprocess.run("sudo systemctl restart NetworkManager 2>/dev/null || sudo service network-manager restart 2>/dev/null", shell=True)
                self.monitor_mode_active = False
                self.current_interface = "wlan0"
                self.monitor_status.set("📡 İzleme Modu: KAPALI")
                self.monitor_label.config(fg="red")
                self.monitor_btn.config(text="AÇ", bg="#330000", fg="red")
                self.target_vars["interface"].set("wlan0")
                self.terminal.insert(tk.END, "[✓] Yönetim moduna dönüldü: wlan0\n")
            except Exception as e:
                self.terminal.insert(tk.END, f"[HATA] {str(e)}\n")
        self.terminal.see(tk.END)
    
    def run_selected_tool(self, category=None):
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
        
        params = {k: v.get() for k, v in self.target_vars.items()}
        
        self.terminal.insert(tk.END, f"\n[{datetime.now().strftime('%H:%M:%S')}] Çalıştırılıyor: {tool.name}\n")
        self.terminal.insert(tk.END, f"[KOMUT] {tool.command}\n")
        self.terminal.insert(tk.END, "-" * 80 + "\n")
        self.terminal.see(tk.END)
        
        self.status_label.config(text=f"Çalışıyor: {tool.name}")
        self.current_output = ""
        self.current_op_id = self.db.add_operation(tool.name, tool.command, params.get("target", ""))
        
        threading.Thread(target=self._run_tool_thread, args=(tool_id, params), daemon=True).start()
    
    def _run_tool_thread(self, tool_id, params):
        result = self.tool_manager.run_tool(tool_id, params)
        if "error" in result:
            self.output_queue.put(f"\n[HATA] {result['error']}\n")
            self.current_output = result['error']
            if self.current_op_id:
                self.db.update_operation(self.current_op_id, "FAILED", result['error'])
        else:
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")
            self.output_queue.put(stdout)
            if stderr:
                self.output_queue.put(f"\n[HATA ÇIKTISI]\n{stderr}\n")
            self.output_queue.put(f"\n[İŞLEM TAMAMLANDI] Çıkış kodu: {result['return_code']}\n")
            self.current_output = stdout + stderr
            if self.current_op_id:
                status = "SUCCESS" if result['return_code'] == 0 else "FAILED"
                self.db.update_operation(self.current_op_id, status, self.current_output[:1000])
                if "open" in stdout.lower() or "vulnerable" in stdout.lower():
                    self._auto_extract_findings(stdout, tool_id, params.get("target", ""))
        self.output_queue.put("\n[>] Hazır. Yeni komut bekleniyor...\n")
        self.root.after(100, lambda: self.status_label.config(text="Hazır"))
    
    def _auto_extract_findings(self, output: str, tool_id: int, target: str):
        tool = self.tool_manager.get_tool(tool_id)
        lines = output.split('\n')
        for line in lines[:20]:
            if "open" in line and "tcp" in line.lower():
                parts = line.split()
                if len(parts) >= 3:
                    self.db.add_finding(1, f"Açık Port: {parts[0]}", "INFO", description=line.strip())
    
    def stop_current_tool(self):
        self.tool_manager.stop_current()
        self.terminal.insert(tk.END, "\n[!] İşlem durduruldu.\n")
        self.terminal.see(tk.END)
        self.status_label.config(text="Durduruldu")
    
    def generate_report(self):
        ops = self.db.get_operations(50)
        findings = self.db.get_findings(limit=50)
        if not ops:
            messagebox.showinfo("Bilgi", "Henüz raporlanacak işlem yok.")
            return
        filepath = self.report_gen.generate_html(ops, findings)
        self.terminal.insert(tk.END, f"\n[✓] Rapor oluşturuldu: {filepath}\n")
        self.terminal.see(tk.END)
        self.report_gen.open_report(filepath)
    
    def ask_ai(self):
        dialog = tk.Toplevel(self.root, bg='#0a0a0a')
        dialog.title("🤖 KERMAN AI ASİSTAN")
        dialog.geometry("600x500")
        
        tk.Label(dialog, text="Sorunuzu yazın:", fg="#00ff00", bg="#0a0a0a", font=("Courier", 12)).pack(pady=10)
        question = tk.Text(dialog, bg='#111', fg='#00ff00', height=5, font=("Courier", 10), insertbackground='#00ff00')
        question.pack(fill="x", padx=10, pady=5)
        
        tk.Label(dialog, text="Yanıt:", fg="#00ff00", bg="#0a0a0a", font=("Courier", 12)).pack(pady=5)
        answer = tk.Text(dialog, bg='#111', fg='#00ff00', height=12, font=("Courier", 10))
        answer.pack(fill="both", expand=True, padx=10, pady=5)
        
        def get_answer():
            q = question.get(1.0, tk.END).strip()
            if not q:
                return
            answer.delete(1.0, tk.END)
            answer.insert(1.0, "Düşünüyorum...")
            dialog.update()
            ans = self.ai_module.ask(q, self.current_output[-500:] if self.current_output else "")
            answer.delete(1.0, tk.END)
            answer.insert(1.0, ans)
        
        def analyze_error():
            if self.current_output:
                ans = self.ai_module.analyze_error(self.current_output)
                answer.delete(1.0, tk.END)
                answer.insert(1.0, f"HATA ANALİZİ:\n\n{ans}")
        
        btn_frame = tk.Frame(dialog, bg='#0a0a0a')
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Sor", command=get_answer, bg="#003300", fg="#00ff00", font=("Courier", 10), width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Hata Analizi", command=analyze_error, bg="#330000", fg="red", font=("Courier", 10), width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Kapat", command=dialog.destroy, bg="#333", fg="white", font=("Courier", 10), width=10).pack(side="left", padx=5)
    
    def start_voice(self):
        if not self.voice_module.is_available():
            messagebox.showwarning("Uyarı", "Ses tanıma kullanılamıyor.\npip install SpeechRecognition pyaudio")
            return
        self.terminal.insert(tk.END, "\n[*] Sesli komut dinleniyor...\n")
        self.terminal.see(tk.END)
        self.voice_module.listen_once(self._process_voice_command)
    
    def _process_voice_command(self, text: str):
        cmd = self.voice_module.process_command(text)
        if cmd.get("tool_id"):
            self.tool_entry.delete(0, tk.END)
            self.tool_entry.insert(0, str(cmd["tool_id"]))
            if cmd.get("target"):
                self.target_vars["target"].set(cmd["target"])
            self.run_selected_tool()
        else:
            self.terminal.insert(tk.END, f"[!] Komut anlaşılamadı: {text}\n")
            self.terminal.see(tk.END)
    
    def update_terminal(self):
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
        if hasattr(self, 'matrix'):
            self.matrix.stop()
