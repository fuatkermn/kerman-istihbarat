#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import threading
import queue

@dataclass
class Tool:
    """Araç tanımı."""
    tool_id: int
    name: str
    category: str
    command: str
    description: str = ""
    requires_root: bool = False

class ToolManager:
    """Araç yönetim sınıfı."""
    
    def __init__(self):
        self.tools: Dict[int, Tool] = {}
        self.categories: Dict[str, List[int]] = {}
        self._load_builtin_tools()
    
    def _load_builtin_tools(self):
        """Yerleşik araçları yükler."""
        
        # WiFi Araçları (1-10)
        wifi_tools = [
            Tool(1, "Airodump-ng - Kablosuz Ağ Tarama", "WiFi", "airodump-ng {interface}", "Kablosuz ağları tarar", True),
            Tool(2, "Aireplay-ng - Bağlantı Kesme", "WiFi", "aireplay-ng -0 0 -a {bssid} {interface}", "Deauth saldırısı", True),
            Tool(3, "Wifite - Otomatik Saldırı", "WiFi", "wifite --kill", "Otomatik WiFi saldırısı", True),
            Tool(4, "Bettercap - Ağ Keşfi", "WiFi", "bettercap -eval 'wifi.recon on'", "Bettercap WiFi keşif", True),
            Tool(5, "MDK4 - Beacon Saldırısı", "WiFi", "mdk4 {interface} b -s 500", "Sahte ağ oluşturma", True),
            Tool(6, "Reaver - WPS Kırma", "WiFi", "reaver -i {interface} -b {bssid} -vv", "WPS PIN kırma", True),
            Tool(7, "Kismet - Pasif Keşif", "WiFi", "kismet -c {interface}", "Pasif WiFi keşif", True),
            Tool(8, "Airgeddon - WiFi Çerçevesi", "WiFi", "airgeddon", "Çok amaçlı WiFi aracı", True),
            Tool(9, "Wash - WPS Ağ Tarama", "WiFi", "wash -i {interface}", "WPS etkin ağları bulur", True),
            Tool(10, "HCXDumpTool - Paket Yakalama", "WiFi", "hcxdumptool -i {interface} -o capture.pcapng", "WPA paket yakalama", True),
        ]
        for t in wifi_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("WiFi", []).append(t.tool_id)
        
        # OSINT Araçları (11-20)
        osint_tools = [
            Tool(11, "Nmap - Hızlı Tarama", "OSINT", "nmap -T4 -F {target}", "Hızlı port taraması"),
            Tool(12, "Nmap - Ayrıntılı Tarama", "OSINT", "nmap -sV -sC -O {target}", "Detaylı servis taraması"),
            Tool(13, "Sherlock - Kullanıcı Adı Arama", "OSINT", "sherlock {target}", "Sosyal medya taraması"),
            Tool(14, "TheHarvester - E-posta/Domain", "OSINT", "theHarvester -d {domain} -b all", "E-posta adresi toplama"),
            Tool(15, "Amass - Alt Domain Keşfi", "OSINT", "amass enum -d {domain}", "Subdomain keşfi"),
            Tool(16, "Subfinder - Alt Domain Bulma", "OSINT", "subfinder -d {domain}", "Hızlı subdomain tarama"),
            Tool(17, "Holehe - E-posta Denetimi", "OSINT", "holehe {target}", "E-posta hesap kontrolü"),
            Tool(18, "Maigret - Sosyal Medya Tarama", "OSINT", "maigret {target}", "Kullanıcı adı sorgulama"),
            Tool(19, "Recon-ng - Web Keşif", "OSINT", "recon-ng", "Web tabanlı keşif"),
            Tool(20, "Whois - Domain Sorgulama", "OSINT", "whois {domain}", "Domain bilgileri"),
        ]
        for t in osint_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("OSINT", []).append(t.tool_id)
        
        # Web Araçları (21-30)
        web_tools = [
            Tool(21, "SQLMap - SQL Enjeksiyon", "Web", "sqlmap -u {target} --batch --dbs", "Otomatik SQL injection"),
            Tool(22, "Gobuster - Dizin Tarama", "Web", "gobuster dir -u {target} -w {wordlist}", "Dizin keşfi"),
            Tool(23, "FFUF - Web Fuzzing", "Web", "ffuf -u {target}/FUZZ -w {wordlist}", "Hızlı web fuzzer"),
            Tool(24, "WPScan - WordPress Tarama", "Web", "wpscan --url {target}", "WordPress güvenlik taraması"),
            Tool(25, "Nikto - Web Sunucu Tarama", "Web", "nikto -h {target}", "Web sunucu açıklıkları"),
            Tool(26, "Nuclei - Zafiyet Tarayıcı", "Web", "nuclei -u {target}", "Şablon tabanlı tarama"),
            Tool(27, "XSStrike - XSS Tarayıcı", "Web", "xsstrike -u {target}", "Gelişmiş XSS tespiti"),
            Tool(28, "Dirb - Dizin Keşfi", "Web", "dirb {target} {wordlist}", "Klasik dizin tarama"),
            Tool(29, "WhatWeb - Teknoloji Tanıma", "Web", "whatweb {target}", "Web teknolojilerini tanır"),
            Tool(30, "Commix - Komut Enjeksiyon", "Web", "commix --url {target}", "Command injection testi"),
        ]
        for t in web_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Web", []).append(t.tool_id)

        # Exploit Araçları (31-35)
        exploit_tools = [
            Tool(31, "Metasploit - Sızma Çerçevesi", "Exploit", "msfconsole -q", "Metasploit Framework", True),
            Tool(32, "SearchSploit - Açıklık Arama", "Exploit", "searchsploit {target}", "Exploit-DB araması"),
            Tool(33, "Hydra - Kaba Kuvvet", "Exploit", "hydra -l {user} -P {wordlist} {target} {service}", "Parola deneme"),
            Tool(34, "John - Parola Kırma", "Exploit", "john --wordlist={wordlist} {hash}", "John the Ripper"),
            Tool(35, "Hashcat - GPU Parola Kırma", "Exploit", "hashcat -m 0 {hash} {wordlist}", "GPU destekli kırma"),
        ]
        for t in exploit_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Exploit", []).append(t.tool_id)
        
        # AD Araçları (36-40)
        ad_tools = [
            Tool(36, "BloodHound - AD Keşif", "AD", "bloodhound-python -d {domain} -u {user} -p '{password}' -c All", "Active Directory haritalama"),
            Tool(37, "Evil-WinRM - Uzak Kabuk", "AD", "evil-winrm -i {target} -u {user} -p '{password}'", "Windows Remote Management"),
            Tool(38, "Impacket-secretsdump", "AD", "secretsdump.py {domain}/{user}:{password}@{target}", "Hash dökme aracı"),
            Tool(39, "Impacket-psexec", "AD", "psexec.py {domain}/{user}:{password}@{target}", "Uzaktan komut çalıştırma"),
            Tool(40, "Kerberoast", "AD", "GetUserSPNs.py {domain}/{user}:{password} -request", "Kerberoasting saldırısı"),
        ]
        for t in ad_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("AD", []).append(t.tool_id)
        
        # Cloud Araçları (41-45)
        cloud_tools = [
            Tool(41, "Trivy - Konteyner Tarama", "Cloud", "trivy image {docker_image}", "Docker imaj tarayıcı"),
            Tool(42, "Prowler - AWS Denetim", "Cloud", "prowler aws", "AWS güvenlik denetimi"),
            Tool(43, "ScoutSuite - Çoklu Bulut", "Cloud", "scout aws", "AWS/Azure/GCP denetimi"),
            Tool(44, "Kubescape - K8s Güvenlik", "Cloud", "kubescape scan", "Kubernetes güvenlik taraması"),
            Tool(45, "TruffleHog - Gizli Anahtar", "Cloud", "trufflehog filesystem .", "Gizli anahtar tarayıcı"),
        ]
        for t in cloud_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Cloud", []).append(t.tool_id)

    def get_tool(self, tool_id: int) -> Optional[Tool]:
        return self.tools.get(tool_id)
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        ids = self.categories.get(category, [])
        return [self.tools[i] for i in ids if i in self.tools]
    
    def get_all_categories(self) -> List[str]:
        return list(self.categories.keys())
    
    def search_tools(self, query: str) -> List[Tool]:
        results = []
        q = query.lower()
        for tool in self.tools.values():
            if q in tool.name.lower() or q in tool.description.lower():
                results.append(tool)
        return results
    
    def run_tool(self, tool_id: int, params: Dict[str, str]) -> Dict:
        """Aracı çalıştırır."""
        tool = self.get_tool(tool_id)
        if not tool:
            return {"error": f"Araç bulunamadı: {tool_id}"}
        
        cmd = tool.command
        for key, value in params.items():
            cmd = cmd.replace(f"{{{key}}}", value)
        
        # Varsayılan değerleri doldur
        cmd = cmd.replace("{interface}", params.get("interface", "wlan0"))
        cmd = cmd.replace("{wordlist}", params.get("wordlist", "/usr/share/wordlists/rockyou.txt"))
        cmd = cmd.replace("{password}", params.get("password", ""))
        cmd = cmd.replace("{docker_image}", params.get("docker_image", ""))
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            return {
                "tool": tool.name,
                "command": cmd,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {"error": "Zaman aşımı (300s)"}
        except Exception as e:
            return {"error": str(e)}
