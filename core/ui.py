#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import subprocess
import re
from datetime import datetime

from core.matrix_bg import MatrixBackground
from core.database import Database
from core.tool_manager import ToolManager
from core.report_generator import ReportGenerator
from core.ai_module import AIModule
from core.voice_module import VoiceModule
from core.helpers import ToolInstaller

class KermanMainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KERMAN İSTİHBARAT v3.0 PROFESSIONAL")
        self.root.geometry("1600x950")
        self.root.configure(bg='#0a0a0a')
        
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
            "channel": tk.StringVar(value="1"),  # YENİ EKLENDİ
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
        self.matrix = MatrixBackground(self.canvas, 1600, 950)
        self.matrix.draw()
        
        main_container = tk.Frame(self.root, bg='#0a0a0a')
        main_container.place(relx=0.5, rely=0.5, anchor="center", width=1550, height=920)
        
        self.create_top_bar(main_container)
        self.create_left_panel(main_container)
        self.create_center_panel(main_container)
        self.create_right_panel(main_container)
        self.create_status_bar(main_container)
        
        self.update_terminal()
    
    def create_top_bar(self, parent):
        top_bar = tk.Frame(parent, bg='#111', height=45)
        top_bar.pack(fill="x", padx=5, pady=5)
        
        title = tk.Label(top_bar, text="⚡ KERMAN İSTİHBARAT v3.0 ⚡", 
                         fg="#00ff00", bg="#111", font=("Courier", 16, "bold"))
        title.pack(side="left", padx=15)
        
        monitor_frame = tk.Frame(top_bar, bg='#111')
        monitor_frame.pack(side="right", padx=15)
        
        self.monitor_status = tk.StringVar(value="📡 İzleme Modu: KAPALI")
        tk.Label(monitor_frame, textvariable=self.monitor_status, fg="red", bg="#111", 
                 font=("Courier", 10)).pack(side="left", padx=5)
        
        self.monitor_btn = tk.Button(monitor_frame, text="AÇ", command=self.toggle_monitor_mode,
                                      bg="#330000", fg="red", font=("Courier", 9, "bold"), 
                                      width=6, cursor="hand2")
        self.monitor_btn.pack(side="left")
        
        tk.Label(top_bar, text="🔍", fg="#00ff00", bg="#111", font=("Arial", 14)).pack(side="right", padx=5)
        tk.Label(top_bar, text="📊", fg="#00ff00", bg="#111", font=("Arial", 14)).pack(side="right", padx=5)
        tk.Label(top_bar, text="⚙️", fg="#00ff00", bg="#111", font=("Arial", 14)).pack(side="right", padx=5)
    
    def create_left_panel(self, parent):
        left_frame = tk.Frame(parent, bg='#111', width=300)
        left_frame.pack(side="left", fill="both", expand=False, padx=5, pady=5)
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="📁 KATEGORİLER", fg="#00ff00", bg="#111", 
                 font=("Courier", 11, "bold")).pack(pady=5)
        
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.pack(fill="both", expand=True, padx=3, pady=3)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#111', borderwidth=0)
        style.configure('TNotebook.Tab', background='#1a1a1a', foreground='#00ff00', 
                        padding=[8, 4], font=('Courier', 9))
        style.map('TNotebook.Tab', background=[('selected', '#003300')])
        
        self.tool_listboxes = {}
        kategoriler = ["WiFi", "OSINT", "Web", "Exploit", "AD", "Cloud", 
                       "DarkWeb", "Blockchain", "IoT", "Forensic", "Spyware", "Scenarios"]
        
        for kat in kategoriler:
            frame = tk.Frame(self.notebook, bg='#0a0a0a')
            self.notebook.add(frame, text=kat)
            
            list_frame = tk.Frame(frame, bg='#0a0a0a')
            list_frame.pack(fill="both", expand=True, padx=2, pady=2)
            
            scrollbar = tk.Scrollbar(list_frame, bg='#333', troughcolor='#111')
            scrollbar.pack(side="right", fill="y")
            
            listbox = tk.Listbox(list_frame, bg='#0a0a0a', fg='#00cc00', 
                                 font=("Courier", 9), selectbackground='#004400',
                                 yscrollcommand=scrollbar.set, relief="flat",
                                 highlightthickness=0)
            listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=listbox.yview)
            
            self.tool_listboxes[kat] = listbox
            
            araclar = self.tool_manager.get_tools_by_category(kat)
            for arac in araclar:
                listbox.insert(tk.END, f"{arac.tool_id:3d}. {arac.name[:35]}")
            
            listbox.bind("<Double-Button-1>", lambda e, c=kat: self.run_selected_tool(c))
        
        cmd_frame = tk.Frame(left_frame, bg='#111')
        cmd_frame.pack(fill="x", padx=5, pady=8)
        
        tk.Label(cmd_frame, text="Araç No:", fg="#00ff00", bg="#111", 
                 font=("Courier", 10)).pack(side="left")
        
        self.tool_entry = tk.Entry(cmd_frame, bg='#1a1a1a', fg='#00ff00', width=5,
                                   font=("Courier", 11), insertbackground='#00ff00',
                                   relief="flat", justify="center")
        self.tool_entry.pack(side="left", padx=5)
        self.tool_entry.bind("<Return>", lambda e: self.run_selected_tool())
        
        tk.Button(cmd_frame, text="▶", command=self.run_selected_tool,
                  bg="#003300", fg="#00ff00", font=("Arial", 10, "bold"),
                  width=3, cursor="hand2", relief="flat").pack(side="left", padx=2)
        
        tk.Button(cmd_frame, text="⬛", command=self.stop_current_tool,
                  bg="#333300", fg="#ffff00", font=("Arial", 10, "bold"),
                  width=3, cursor="hand2", relief="flat").pack(side="left", padx=2)
    
    def create_center_panel(self, parent):
        center_frame = tk.Frame(parent, bg='#0a0a0a', width=450)
        center_frame.pack(side="left", fill="both", expand=False, padx=5, pady=5)
        center_frame.pack_propagate(False)
        
        target_card = tk.Frame(center_frame, bg='#1a0000', relief="solid", bd=1)
        target_card.pack(fill="x", padx=5, pady=5)
        
        tk.Label(target_card, text="🎯 HEDEF BİLGİLERİ", fg="red", bg="#1a0000", 
                 font=("Courier", 11, "bold")).pack(pady=5)
        
        fields = [
            ("Hedef IP/URL", "target"),
            ("Arayüz", "interface"),
            ("BSSID/MAC", "bssid"),
            ("Domain", "domain"),
            ("Kullanıcı", "user"),
            ("Port", "port"),
            ("Parola", "password"),
            ("Hash", "hash"),
        ]
        
        for label, var_name in fields:
            f = tk.Frame(target_card, bg='#1a0000')
            f.pack(fill="x", padx=10, pady=3)
            tk.Label(f, text=f"{label}:", fg="red", bg="#1a0000", 
                     font=("Courier", 9), width=10, anchor="w").pack(side="left")
            entry = tk.Entry(f, textvariable=self.target_vars[var_name], 
                            bg='#0a0a0a', fg='#ff8888', insertbackground='red',
                            font=("Courier", 9), relief="flat")
            entry.pack(side="left", fill="x", expand=True)
        
        wl_frame = tk.Frame(target_card, bg='#1a0000')
        wl_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(wl_frame, text="Wordlist:", fg="red", bg="#1a0000", 
                 font=("Courier", 9), width=10, anchor="w").pack(side="left")
        tk.Entry(wl_frame, textvariable=self.target_vars["wordlist"], 
                bg='#0a0a0a', fg='#ff8888', font=("Courier", 8)).pack(side="left", fill="x", expand=True)
        tk.Button(wl_frame, text="📁", command=self.browse_wordlist,
                  bg="#330000", fg="red", width=3, cursor="hand2", relief="flat").pack(side="left", padx=2)
        
        btn_frame = tk.Frame(center_frame, bg='#0a0a0a')
        btn_frame.pack(fill="x", padx=5, pady=10)
        
        buttons = [
            ("📊 RAPOR", self.generate_report, "#000033", "#00ccff"),
            ("🤖 AI SOR", self.ask_ai, "#330033", "#ff00ff"),
            ("🎤 SESLİ", self.start_voice, "#003333", "#00ffff"),
            ("💾 KAYDET", self.save_target, "#333300", "#ffff00"),
            ("🔧 KONTROL", self.check_tools, "#333333", "#ffffff"),
        ]
        
        for text, cmd, bg, fg in buttons:
            tk.Button(btn_frame, text=text, command=cmd, bg=bg, fg=fg,
                      font=("Courier", 9, "bold"), cursor="hand2", relief="flat",
                      height=2).pack(side="left", fill="x", expand=True, padx=2)
        
        stats_frame = tk.Frame(center_frame, bg='#111')
        stats_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(stats_frame, text="📈 İSTATİSTİKLER", fg="#00ff00", bg="#111", 
                 font=("Courier", 10, "bold")).pack(pady=3)
        
        self.stats_text = tk.Text(stats_frame, bg='#0a0a0a', fg='#00cc00', 
                                   font=("Courier", 8), height=6, relief="flat")
        self.stats_text.pack(fill="x", padx=5, pady=3)
        self.update_stats()
    
    def create_right_panel(self, parent):
        right_frame = tk.Frame(parent, bg='#0a0a0a')
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        term_header = tk.Frame(right_frame, bg='#111', height=30)
        term_header.pack(fill="x")
        tk.Label(term_header, text="📟 TERMİNAL ÇIKTISI", fg="#00ff00", bg="#111", 
                 font=("Courier", 11, "bold")).pack(side="left", padx=10)
        tk.Button(term_header, text="🧹", command=self.clear_terminal,
                  bg="#222", fg="#00ff00", width=3, cursor="hand2", relief="flat").pack(side="right", padx=5)
        
        self.terminal = scrolledtext.ScrolledText(right_frame, bg='#0a0a0a', fg='#00ff00',
                                                  font=("Courier", 9), insertbackground='#00ff00',
                                                  relief="flat")
        self.terminal.pack(fill="both", expand=True)
        
        self.terminal.insert(tk.END, "╔" + "═" * 100 + "╗\n")
        self.terminal.insert(tk.END, "║" + " KERMAN İSTİHBARAT v3.0 PROFESSIONAL ".center(100) + "║\n")
        self.terminal.insert(tk.END, "╠" + "═" * 100 + "╣\n")
        self.terminal.insert(tk.END, "║ " + "Toplam Araç: 350+ | Kategori: 12 | Hazır".ljust(99) + "║\n")
        self.terminal.insert(tk.END, "╚" + "═" * 100 + "╝\n\n")
        self.terminal.insert(tk.END, "► Sistem hazır. Araç numarası girin veya çift tıklayın.\n\n")
        self.terminal.see(tk.END)
    
    def create_status_bar(self, parent):
        status = tk.Frame(parent, bg='#111', height=25)
        status.pack(fill="x", side="bottom", padx=5, pady=3)
        
        self.status_label = tk.Label(status, text="● Hazır", fg="#00ff00", bg="#111", 
                                     font=("Courier", 9), anchor="w")
        self.status_label.pack(side="left", padx=10)
        
        self.time_label = tk.Label(status, text="", fg="#666", bg="#111", font=("Courier", 9))
        self.time_label.pack(side="right", padx=10)
        self.update_time()
    
    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)
    
    def update_stats(self):
        ops = self.db.get_operations(100)
        success = sum(1 for o in ops if o.get('status') == 'SUCCESS')
        failed = sum(1 for o in ops if o.get('status') == 'FAILED')
        
        stats = f"""
Toplam İşlem: {len(ops)}
Başarılı: {success}
Başarısız: {failed}
Son İşlem: {ops[0]['tool_name'][:30] if ops else 'Yok'}
"""
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
    
    def browse_wordlist(self):
        filename = filedialog.askopenfilename(title="Parola Listesi Seç", 
                                               filetypes=[("Text files", "*.txt")])
        if filename:
            self.target_vars["wordlist"].set(filename)
    
    def save_target(self):
        name = self.target_vars["target"].get() or "İsimsiz"
        self.db.add_target(name, 
                          ip=self.target_vars["target"].get(),
                          domain=self.target_vars["domain"].get())
        self.terminal.insert(tk.END, f"[✓] Hedef kaydedildi: {name}\n")
        self.terminal.see(tk.END)
        self.update_stats()
    
    def clear_terminal(self):
        self.terminal.delete(1.0, tk.END)
    
    def toggle_monitor_mode(self):
        if not self.monitor_mode_active:
            self.terminal.insert(tk.END, f"\n[*] {self.current_interface} monitör moda alınıyor...\n")
            try:
                subprocess.run("sudo airmon-ng check kill 2>/dev/null", shell=True)
                result = subprocess.run(f"sudo airmon-ng start {self.current_interface}", 
                                       shell=True, capture_output=True, text=True)
                if "monitor mode enabled" in result.stdout.lower():
                    match = re.search(r'([a-zA-Z0-9]+mon)', result.stdout)
                    if match:
                        self.current_interface = match.group(1)
                self.monitor_mode_active = True
                self.monitor_status.set(f"📡 İzleme Modu: AÇIK ({self.current_interface})")
                self.monitor_btn.config(text="KAPAT", bg="#003300", fg="green")
                self.target_vars["interface"].set(self.current_interface)
                self.terminal.insert(tk.END, f"[✓] Monitör mod aktif: {self.current_interface}\n")
            except Exception as e:
                self.terminal.insert(tk.END, f"[HATA] {str(e)}\n")
        else:
            self.terminal.insert(tk.END, f"\n[*] Yönetim moduna dönülüyor...\n")
            try:
                subprocess.run(f"sudo airmon-ng stop {self.current_interface}", shell=True)
                subprocess.run("sudo systemctl restart NetworkManager 2>/dev/null", shell=True)
                self.monitor_mode_active = False
                self.current_interface = "wlan0"
                self.monitor_status.set("📡 İzleme Modu: KAPALI")
                self.monitor_btn.config(text="AÇ", bg="#330000", fg="red")
                self.target_vars["interface"].set("wlan0")
                self.terminal.insert(tk.END, "[✓] Yönetim moduna dönüldü\n")
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
        
        cmd_name = tool.command.split()[0] if tool.command else ""
        if not ToolInstaller.check_tool(cmd_name):
            if messagebox.askyesno("Eksik Araç", f"'{cmd_name}' kurulu değil. Şimdi kurulsun mu?"):
                self.terminal.insert(tk.END, f"\n[*] {cmd_name} kuruluyor...\n")
                success, msg = ToolInstaller.install_tool(cmd_name)
                self.terminal.insert(tk.END, f"    {'✓' if success else '✗'} {msg}\n")
                if not success:
                    return
        
        params = {k: v.get() for k, v in self.target_vars.items()}
        
        self.terminal.insert(tk.END, f"\n[{datetime.now().strftime('%H:%M:%S')}] {tool.name}\n")
        self.terminal.insert(tk.END, f"[CMD] {tool.command}\n")
        self.terminal.insert(tk.END, "─" * 100 + "\n")
        self.terminal.see(tk.END)
        
        self.status_label.config(text=f"● Çalışıyor: {tool.name}")
        self.current_output = ""
        self.current_op_id = self.db.add_operation(tool.name, tool.command, params.get("target", ""))
        
        threading.Thread(target=self._run_tool_thread, args=(tool_id, params), daemon=True).start()
    
    def _run_tool_thread(self, tool_id, params):
        result = self.tool_manager.run_tool(tool_id, params)
        
        if "error" in result:
            self.output_queue.put(f"\n[HATA] {result['error']}\n")
            if self.current_op_id:
                self.db.update_operation(self.current_op_id, "FAILED", result['error'])
        else:
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")
            
            if stdout:
                self.output_queue.put(stdout)
            if stderr:
                self.output_queue.put(f"\n[STDERR]\n{stderr}\n")
            
            return_code = result.get("return_code", -1)
            if return_code == 0:
                self.output_queue.put(f"\n[✓] İşlem başarıyla tamamlandı.\n")
            else:
                self.output_queue.put(f"\n[!] İşlem hata koduyla tamamlandı: {return_code}\n")
            
            if self.current_op_id:
                status = "SUCCESS" if return_code == 0 else "FAILED"
                self.db.update_operation(self.current_op_id, status, stdout[:500] if stdout else "")
        
        self.output_queue.put("\n► Hazır. Yeni komut bekleniyor...\n")
        self.root.after(100, lambda: self.status_label.config(text="● Hazır"))
        self.root.after(100, self.update_stats)
    
    def stop_current_tool(self):
        self.tool_manager.stop_current()
        self.terminal.insert(tk.END, "\n[!] İşlem durduruldu.\n")
        self.terminal.see(tk.END)
        self.status_label.config(text="● Durduruldu")
    
    def generate_report(self):
        ops = self.db.get_operations(50)
        findings = self.db.get_findings(limit=50)
        if not ops:
            messagebox.showinfo("Bilgi", "Raporlanacak işlem yok.")
            return
        filepath = self.report_gen.generate_html(ops, findings)
        self.terminal.insert(tk.END, f"\n[✓] Rapor: {filepath}\n")
        self.report_gen.open_report(filepath)
    
    def ask_ai(self):
        dialog = tk.Toplevel(self.root, bg='#111')
        dialog.title("🤖 KERMAN AI ASİSTAN")
        dialog.geometry("700x550")
        
        tk.Label(dialog, text="Sorunuz:", fg="#00ff00", bg="#111", font=("Courier", 12)).pack(pady=10)
        question = tk.Text(dialog, bg='#1a1a1a', fg='#00ff00', height=5, 
                           font=("Courier", 10), insertbackground='#00ff00')
        question.pack(fill="x", padx=10, pady=5)
        
        tk.Label(dialog, text="Yanıt:", fg="#00ff00", bg="#111", font=("Courier", 12)).pack(pady=5)
        answer = tk.Text(dialog, bg='#1a1a1a', fg='#00ff00', height=15, font=("Courier", 10))
        answer.pack(fill="both", expand=True, padx=10, pady=5)
        
        def get_answer():
            q = question.get(1.0, tk.END).strip()
            if q:
                ans = self.ai_module.ask(q, self.current_output[-500:])
                answer.delete(1.0, tk.END)
                answer.insert(1.0, ans)
        
        tk.Button(dialog, text="Sor", command=get_answer, bg="#003300", fg="#00ff00",
                  font=("Courier", 10), width=10).pack(pady=10)
        tk.Button(dialog, text="Kapat", command=dialog.destroy, bg="#333", fg="white",
                  font=("Courier", 10), width=10).pack(pady=5)
    
    def start_voice(self):
        self.terminal.insert(tk.END, "\n[*] Sesli komut dinleniyor...\n")
        self.voice_module.listen_once(self._process_voice_command)
    
    def _process_voice_command(self, text: str):
        self.terminal.insert(tk.END, f"[✓] Algılanan: {text}\n")
        if "tarama" in text.lower():
            self.tool_entry.delete(0, tk.END)
            self.tool_entry.insert(0, "26")
            self.run_selected_tool()
    
    def check_tools(self):
        self.terminal.insert(tk.END, "\n[*] Araçlar kontrol ediliyor...\n")
        self.terminal.see(tk.END)
        
        def check_thread():
            installed = []
            missing = []
            
            for tool_id, tool in self.tool_manager.tools.items():
                cmd_name = tool.command.split()[0] if tool.command else ""
                if ToolInstaller.check_tool(cmd_name):
                    installed.append(tool.name)
                else:
                    missing.append((tool.name, cmd_name))
            
            self.output_queue.put(f"\n[✓] Kurulu araçlar: {len(installed)}\n")
            self.output_queue.put(f"[!] Eksik araçlar: {len(missing)}\n\n")
            
            if missing:
                self.output_queue.put("Eksik araçlar (ilk 30):\n")
                for name, cmd in missing[:30]:
                    self.output_queue.put(f"  - {name} ({cmd})\n")
                self.output_queue.put("\n[*] Kurmak için araç numarasını girip çalıştırdığınızda otomatik kurulum önerilecektir.\n")
            
        threading.Thread(target=check_thread, daemon=True).start()
    
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
