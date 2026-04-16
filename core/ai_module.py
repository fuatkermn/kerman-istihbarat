#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import re

class AIModule:
    def __init__(self):
        self.ollama_available = self._check_ollama()
        self.model = "llama3.2"
    
    def _check_ollama(self) -> bool:
        result = subprocess.run("which ollama", shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    def ask(self, question: str, context: str = "") -> str:
        if not self.ollama_available:
            return self._offline_response(question)
        
        try:
            prompt = f"""Sen KERMAN İSTİHBARAT'ın yapay zeka asistanısın. Bir pentest ve siber güvenlik uzmanısın.
            
Soru: {question}

Bağlam: {context}

Yanıt (Türkçe, kısa ve öz):"""
            
            result = subprocess.run(f"ollama run {self.model} \"{prompt}\"", shell=True, capture_output=True, text=True, timeout=60)
            return result.stdout.strip()
        except:
            return self._offline_response(question)
    
    def _offline_response(self, question: str) -> str:
        q = question.lower()
        responses = {
            "nmap": "Nmap kullanımı: nmap -sV -sC -O hedef (detaylı tarama), nmap -p- hedef (tüm portlar)",
            "sql": "SQLMap: sqlmap -u 'http://hedef/sayfa?id=1' --dbs",
            "wifi": "WiFi saldırısı: airmon-ng start wlan0, airodump-ng wlan0mon, aireplay-ng -0 0 -a BSSID wlan0mon",
            "hashcat": "Hashcat: hashcat -m 0 hash.txt rockyou.txt (MD5), -m 1000 (NTLM)",
            "metasploit": "Metasploit: msfconsole, search exploit, use exploit/..., set RHOSTS hedef, run",
            "hydra": "Hydra: hydra -l kullanici -P wordlist.txt hedef ssh",
            "john": "John the Ripper: john --wordlist=rockyou.txt hash.txt",
        }
        for k, v in responses.items():
            if k in q:
                return v
        return "Bu konuda bilgim yok. Lütfen nmap, sqlmap, wifi, hashcat, metasploit, hydra veya john hakkında soru sorun."
    
    def analyze_error(self, error_output: str) -> str:
        error_lower = error_output.lower()
        if "permission denied" in error_lower:
            return "Yetki hatası: sudo ile çalıştırmayı deneyin."
        elif "command not found" in error_lower:
            return "Araç kurulu değil: sudo apt install [araç-adı] ile kurun."
        elif "timeout" in error_lower:
            return "Zaman aşımı: Hedef yanıt vermiyor veya ağ bağlantısı yavaş."
        elif "connection refused" in error_lower:
            return "Bağlantı reddedildi: Hedef port kapalı veya servis çalışmıyor."
        elif "no such file" in error_lower:
            return "Dosya bulunamadı: Dosya yolunu kontrol edin."
        else:
            return "Bilinmeyen hata. Çıktıyı inceleyin."
    
    def suggest_exploit(self, service: str, version: str) -> str:
        return f"searchsploit {service} {version} ile exploit araştırması yapın."
