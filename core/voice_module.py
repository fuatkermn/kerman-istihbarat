#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import queue

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

class VoiceModule:
    def __init__(self, output_queue: queue.Queue = None):
        self.output_queue = output_queue
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.callback = None
        
        if SR_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
            except:
                pass
    
    def is_available(self) -> bool:
        return SR_AVAILABLE and self.recognizer is not None and self.microphone is not None
    
    def listen_once(self, callback, language: str = "tr-TR"):
        if not self.is_available():
            if self.output_queue:
                self.output_queue.put("[!] Ses tanıma kullanılamıyor. speech_recognition kurun: pip install SpeechRecognition pyaudio\n")
            return
        
        self.callback = callback
        
        def _listen():
            try:
                with self.microphone as source:
                    if self.output_queue:
                        self.output_queue.put("[*] Dinleniyor... (5 saniye)\n")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        text = self.recognizer.recognize_google(audio, language=language)
                        if self.output_queue:
                            self.output_queue.put(f"[✓] Algılanan: {text}\n")
                        if self.callback:
                            self.callback(text)
                    except sr.WaitTimeoutError:
                        if self.output_queue:
                            self.output_queue.put("[!] Ses algılanmadı.\n")
                    except sr.UnknownValueError:
                        if self.output_queue:
                            self.output_queue.put("[!] Anlaşılamadı.\n")
            except Exception as e:
                if self.output_queue:
                    self.output_queue.put(f"[!] Ses hatası: {str(e)}\n")
        
        threading.Thread(target=_listen, daemon=True).start()
    
    def process_command(self, text: str) -> dict:
        text_lower = text.lower()
        if "nmap" in text_lower or "tarama" in text_lower:
            return {"tool_id": 11, "target": self._extract_target(text)}
        elif "sql" in text_lower or "enjeksiyon" in text_lower:
            return {"tool_id": 21, "target": self._extract_target(text)}
        elif "wifi" in text_lower or "kablosuz" in text_lower:
            return {"tool_id": 1, "interface": "wlan0"}
        elif "metasploit" in text_lower:
            return {"tool_id": 31, "action": "start"}
        else:
            return {"action": "unknown"}
    
    def _extract_target(self, text: str) -> str:
        import re
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        domain_pattern = r'\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b'
        ip_match = re.search(ip_pattern, text)
        if ip_match:
            return ip_match.group(0)
        domain_match = re.search(domain_pattern, text)
        if domain_match:
            return domain_match.group(0)
        return ""
