# 1. Başlık kısmı (create_header metodunda)
title = tk.Label(header, text="⚡ KERMAN İSTİHBARAT ÇERÇEVESİ ⚡",
                 fg="#00ff00", bg="#0a0a0a", font=("Courier", 16, "bold"))

# 2. Hedef paneli başlığı (create_right_panel metodunda)
target_frame = tk.LabelFrame(right_frame, text="🎯 HEDEF BİLGİLERİ",
                             fg="red", bg="#0a0a0a", font=("Courier", 12, "bold"),
                             relief="solid", bd=2)

# 3. Alan etiketleri
fields = [
    ("Hedef IP/URL:", "target"),
    ("Ağ Arayüzü:", "interface"),
    ("BSSID/MAC:", "bssid"),
    ("Domain:", "domain"),
    ("Kullanıcı Adı:", "user"),
    ("Port:", "port"),
]

# 4. Wordlist etiketi
tk.Label(wl_frame, text="Parola Listesi:", fg="red", bg="#0a0a0a", width=12, anchor="w").pack(side="left")

# 5. Terminal başlığı
term_frame = tk.LabelFrame(right_frame, text="📟 UÇ BİRİM ÇIKTISI",
                           fg="#00ff00", bg="#0a0a0a", font=("Courier", 12, "bold"))

# 6. Terminal başlangıç mesajı
self.terminal.insert(tk.END, "╔" + "═" * 78 + "╗\n")
self.terminal.insert(tk.END, "║" + " KERMAN İSTİHBARAT UÇ BİRİMİ ".center(78) + "║\n")
self.terminal.insert(tk.END, "╚" + "═" * 78 + "╝\n\n")
self.terminal.insert(tk.END, "[*] Sistem hazır. Araç numarası girin veya listeden seçin.\n\n")

# 7. Durum çubuğu
self.status_label.config(text="Hazır")

# 8. Çalıştırma mesajları (_run_tool_thread metodunda)
self.terminal.insert(tk.END, f"\n[{datetime.now().strftime('%H:%M:%S')}] Çalıştırılıyor: {tool.name}\n")
self.terminal.insert(tk.END, f"[KOMUT] {tool.command}\n")
self.terminal.insert(tk.END, "-" * 80 + "\n")

# 9. Tamamlanma mesajı
self.output_queue.put(f"\n[İŞLEM TAMAMLANDI] Çıkış kodu: {result['return_code']}\n")
self.output_queue.put("\n[>] Hazır. Yeni komut bekleniyor...\n")
