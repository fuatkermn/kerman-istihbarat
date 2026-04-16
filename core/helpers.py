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
            Tool(1, "Airodump-ng - WiFi Tarama", "WiFi", "airodump-ng {interface}", "Kablosuz ağ tarama", True),
            Tool(2, "Aireplay-ng - Deauth", "WiFi", "aireplay-ng -0 0 -a {bssid} {interface}", "Deauth saldırısı", True),
            Tool(3, "Wifite - Otomatik", "WiFi", "wifite --kill", "Otomatik WiFi saldırısı", True),
            Tool(4, "Bettercap", "WiFi", "bettercap -eval 'wifi.recon on'", "Bettercap WiFi keşif", True),
            Tool(5, "MDK4 - Beacon Flood", "WiFi", "mdk4 {interface} b -s 500", "Beacon flood saldırısı", True),
            Tool(6, "Reaver - WPS", "WiFi", "reaver -i {interface} -b {bssid} -vv", "WPS PIN kırma", True),
            Tool(7, "Kismet", "WiFi", "kismet -c {interface}", "Pasif WiFi keşif", True),
            Tool(8, "Airgeddon", "WiFi", "airgeddon", "WiFi framework", True),
            Tool(9, "Wash - WPS Tarama", "WiFi", "wash -i {interface}", "WPS ağ tarama", True),
            Tool(10, "HCXDumpTool", "WiFi", "hcxdumptool -i {interface} -o capture.pcapng", "Paket yakalama", True),
        ]
        for t in wifi_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("WiFi", []).append(t.tool_id)
        
        # OSINT Araçları (11-20)
        osint_tools = [
            Tool(11, "Nmap - Hızlı", "OSINT", "nmap -T4 -F {target}", "Hızlı port tarama"),
            Tool(12, "Nmap - Detaylı", "OSINT", "nmap -sV -sC -O {target}", "Detaylı tarama"),
            Tool(13, "Sherlock", "OSINT", "sherlock {target}", "Kullanıcı adı arama"),
            Tool(14, "TheHarvester", "OSINT", "theHarvester -d {domain} -b all", "E-posta/subdomain"),
            Tool(15, "Amass", "OSINT", "amass enum -d {domain}", "Subdomain keşfi"),
            Tool(16, "Subfinder", "OSINT", "subfinder -d {domain}", "Subdomain bulucu"),
            Tool(17, "Holehe", "OSINT", "holehe {target}", "E-posta kontrol"),
            Tool(18, "Maigret", "OSINT", "maigret {target}", "Sosyal medya tarama"),
            Tool(19, "Recon-ng", "OSINT", "recon-ng", "Web keşif"),
            Tool(20, "Whois", "OSINT", "whois {domain}", "Domain bilgisi"),
        ]
        for t in osint_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("OSINT", []).append(t.tool_id)
        
        # Web Araçları (21-30)
        web_tools = [
            Tool(21, "SQLMap", "Web", "sqlmap -u {target} --batch --dbs", "SQL injection"),
            Tool(22, "Gobuster", "Web", "gobuster dir -u {target} -w {wordlist}", "Dizin brute force"),
            Tool(23, "FFUF", "Web", "ffuf -u {target}/FUZZ -w {wordlist}", "Web fuzzer"),
            Tool(24, "WPScan", "Web", "wpscan --url {target}", "WordPress tarayıcı"),
            Tool(25, "Nikto", "Web", "nikto -h {target}", "Web sunucu tarama"),
            Tool(26, "Nuclei", "Web", "nuclei -u {target}", "Zafiyet tarayıcı"),
            Tool(27, "XSStrike", "Web", "xsstrike -u {target}", "XSS tarayıcı"),
            Tool(28, "Dirb", "Web", "dirb {target} {wordlist}", "Dizin tarama"),
            Tool(29, "WhatWeb", "Web", "whatweb {target}", "Teknoloji tanıma"),
            Tool(30, "Commix", "Web", "commix --url {target}", "Command injection"),
        ]
        for t in web_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Web", []).append(t.tool_id)

        # Exploit Araçları (31-35)
        exploit_tools = [
            Tool(31, "Metasploit", "Exploit", "msfconsole -q", "Metasploit Framework", True),
            Tool(32, "SearchSploit", "Exploit", "searchsploit {target}", "Exploit-DB arama"),
            Tool(33, "Hydra", "Exploit", "hydra -l {user} -P {wordlist} {target} {service}", "Brute force aracı"),
            Tool(34, "John", "Exploit", "john --wordlist={wordlist} {hash}", "Şifre kırma"),
            Tool(35, "Hashcat", "Exploit", "hashcat -m 0 {hash} {wordlist}", "GPU şifre kırma"),
        ]
        for t in exploit_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Exploit", []).append(t.tool_id)

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
