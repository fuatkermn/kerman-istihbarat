#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import platform
import subprocess
from typing import Dict, List, Optional

class SystemInfo:
    @staticmethod
    def get_summary() -> str:
        info = []
        info.append(f"İşletim Sistemi: {platform.system()} {platform.release()}")
        info.append(f"Hostname: {socket.gethostname()}")
        try:
            import netifaces
            gateways = netifaces.gateways()
            default_iface = gateways['default'][netifaces.AF_INET][1]
            info.append(f"Varsayılan Arayüz: {default_iface}")
        except:
            info.append("Varsayılan Arayüz: wlan0")
        try:
            import psutil
            mem = psutil.virtual_memory()
            info.append(f"RAM: {mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB")
        except:
            pass
        return "\n".join(info)
    
    @staticmethod
    def get_interfaces() -> List[Dict]:
        interfaces = []
        try:
            import netifaces
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    interfaces.append({'name': iface, 'ip': addrs[netifaces.AF_INET][0]['addr']})
        except:
            pass
        return interfaces

class CommandExecutor:
    @staticmethod
    def run(command: str, timeout: int = 300) -> Dict:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
            return {"command": command, "return_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "success": result.returncode == 0}
        except subprocess.TimeoutExpired:
            return {"error": f"Zaman aşımı ({timeout}s)"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def check_tool(tool_name: str) -> bool:
        result = subprocess.run(f"which {tool_name}", shell=True, capture_output=True, text=True)
        return result.returncode == 0

class ProgressTracker:
    def __init__(self, total: int):
        self.total = total
        self.current = 0
        self.start_time = time.time()
    
    def update(self, step: int = 1) -> float:
        self.current += step
        return (self.current / self.total) * 100
    
    def eta(self) -> float:
        if self.current == 0:
            return 0
        elapsed = time.time() - self.start_time
        return (elapsed / self.current) * (self.total - self.current)

class ToolInstaller:
    """Eksik araçları tespit eder ve kurar."""
    
    TOOL_PACKAGES = {
        # WiFi Araçları
        "airodump-ng": "aircrack-ng",
        "aireplay-ng": "aircrack-ng", 
        "aircrack-ng": "aircrack-ng",
        "airmon-ng": "aircrack-ng",
        "wifite": "wifite",
        "bettercap": "bettercap",
        "mdk4": "mdk4",
        "reaver": "reaver",
        "kismet": "kismet",
        "airgeddon": "airgeddon",
        "wash": "reaver",
        "hcxdumptool": "hcxtools",
        "hcxpcaptool": "hcxtools",
        "pyrit": "pyrit",
        "cowpatty": "cowpatty",
        "eaphammer": "eaphammer",
        "wifipumpkin3": "wifipumpkin3",
        "fluxion": "fluxion",
        "linset": "linset",
        "wpspin": "wpspin",
        "pixiewps": "pixiewps",
        "airssl": "airssl",
        "airjack": "airjack",
        "wepbuster": "wepbuster",
        "fern-wifi-cracker": "fern-wifi-cracker",
        "ghost-phisher": "ghost-phisher",
        "wifi-honey": "wifi-honey",
        
        # OSINT Araçları
        "nmap": "nmap",
        "sherlock": "sherlock",
        "theHarvester": "theharvester",
        "amass": "amass",
        "subfinder": "subfinder",
        "holehe": "holehe",
        "maigret": "maigret",
        "recon-ng": "recon-ng",
        "whois": "whois",
        "shodan": "shodan",
        "censys": "censys",
        "spiderfoot": "spiderfoot",
        "maltego": "maltego",
        "photon": "photon",
        "trufflehog": "trufflehog",
        "gitrob": "gitrob",
        "twint": "twint",
        "instaloader": "instaloader",
        "youtube-dl": "youtube-dl",
        "exiftool": "exiftool",
        "metagoofil": "metagoofil",
        "foca": "foca",
        "tinfoleak": "tinfoleak",
        "osintgram": "osintgram",
        "social-analyzer": "social-analyzer",
        "dmitry": "dmitry",
        "masscan": "masscan",
        "rustscan": "rustscan",
        "autorecon": "autorecon",
        "sparta": "sparta",
        "legion": "legion",
        "faraday": "faraday",
        "armitage": "armitage",
        "littlebrother": "littlebrother",
        
        # Web Araçları
        "sqlmap": "sqlmap",
        "gobuster": "gobuster",
        "ffuf": "ffuf",
        "wpscan": "wpscan",
        "nikto": "nikto",
        "nuclei": "nuclei",
        "xsstrike": "xsstrike",
        "dirb": "dirb",
        "whatweb": "whatweb",
        "commix": "commix",
        "burpsuite": "burpsuite",
        "zaproxy": "zaproxy",
        "skipfish": "skipfish",
        "wapiti": "wapiti",
        "vega": "vega",
        "arachni": "arachni",
        "wfuzz": "wfuzz",
        "dirbuster": "dirbuster",
        "joomscan": "joomscan",
        "droopescan": "droopescan",
        "cmsmap": "cmsmap",
        "magescan": "magescan",
        "pscan": "pscan",
        "dalfox": "dalfox",
        "xspear": "xspear",
        "openredirect": "openredirect",
        "crlfuzz": "crlfuzz",
        "ssrfmap": "ssrfmap",
        "xxeinjector": "xxeinjector",
        "lfisuite": "lfisuite",
        "nosqlmap": "nosqlmap",
        "graphqlmap": "graphqlmap",
        "sstimap": "sstimap",
        "jwt_tool": "jwt-tool",
        "corsy": "corsy",
        "arjun": "arjun",
        "paramspider": "paramspider",
        "linkfinder": "linkfinder",
        "secretfinder": "secretfinder",
        "subjack": "subjack",
        "aquatone": "aquatone",
        
        # Exploit Araçları
        "metasploit": "metasploit-framework",
        "msfconsole": "metasploit-framework",
        "searchsploit": "exploitdb",
        "hydra": "hydra",
        "john": "john",
        "hashcat": "hashcat",
        "beef-xss": "beef-xss",
        "responder": "responder",
        "crackmapexec": "crackmapexec",
        "setoolkit": "set",
        "empire": "powershell-empire",
        "covenant": "covenant",
        "merlin": "merlin-agent",
        "mimikatz": "mimikatz",
        "lazagne": "lazagne",
        "powersploit": "powersploit",
        "nishang": "nishang",
        "veil": "veil",
        "shellter": "shellter",
        "msfvenom": "metasploit-framework",
        "arsenal": "arsenal",
        "routersploit": "routersploit",
        "linux-exploit-suggester": "linux-exploit-suggester",
        "windows-exploit-suggester": "windows-exploit-suggester",
        "linpeas": "peass",
        "winpeas": "peass",
        "chisel": "chisel",
        "ngrok": "ngrok",
        "socat": "socat",
        "netcat": "netcat-openbsd",
        "ncat": "nmap",
        "rustscan": "rustscan",
        "autorecon": "autorecon",
        "brutespray": "brutespray",
        "crowbar": "crowbar",
        "medusa": "medusa",
        "peass-ng": "peass",
        "gtfobins": "gtfobins",
        "lolbas": "lolbas",
        "pwnkit": "pwnkit",
        "dirtypipe": "dirtypipe",
        "log4j-scan": "log4j-scan",
        "spring4shell-scan": "spring4shell-scan",
        "heartbleed": "heartbleed",
        "shellshock-scan": "shellshock-scan",
        "eternalblue-scan": "eternalblue-scan",
        "bluekeep-scan": "bluekeep-scan",
        "smbghost-scan": "smbghost-scan",
        "zerologon-scan": "zerologon-scan",
        "printnightmare-scan": "printnightmare-scan",
        "hivenightmare": "hivenightmare",
        "sam-the-admin": "sam-the-admin",
        "nopac": "nopac",
        "petitpotam": "petitpotam",
        "dfscoerce": "dfscoerce",
        "shadowcoerce": "shadowcoerce",
        
        # Active Directory Araçları
        "bloodhound-python": "bloodhound",
        "evil-winrm": "evil-winrm",
        "secretsdump.py": "impacket-scripts",
        "psexec.py": "impacket-scripts",
        "GetUserSPNs.py": "impacket-scripts",
        "GetNPUsers.py": "impacket-scripts",
        "Rubeus.exe": "rubeus",
        "mimikatz.exe": "mimikatz",
        "powerview": "powerview",
        "adrecon": "adrecon",
        "adexplorer": "adexplorer",
        "ldapdomaindump": "ldapdomaindump",
        "enum4linux": "enum4linux",
        "smbclient": "smbclient",
        "smbmap": "smbmap",
        "rpcclient": "samba-client",
        "netexec": "netexec",
        "certipy": "certipy-ad",
        "gettgtpkinit.py": "pkinit-tools",
        "passthecert.py": "passthecert",
        "coercer": "coercer",
        "mitm6": "mitm6",
        "inveigh": "inveigh",
        "ntlmrelayx.py": "impacket-scripts",
        "petitpotam.py": "petitpotam",
        "printerbug.py": "printerbug",
        "dfscoerce.py": "dfscoerce",
        "shadowcoerce.py": "shadowcoerce",
        "rbcd.py": "rbcd",
        
        # Cloud Araçları
        "trivy": "trivy",
        "prowler": "prowler",
        "scout": "scoutsuite",
        "kubescape": "kubescape",
        "trufflehog": "trufflehog",
        "cloudsploit": "cloudsploit",
        "cloudmapper": "cloudmapper",
        "pacu": "pacu",
        "aws": "awscli",
        "gcloud": "google-cloud-cli",
        "az": "azure-cli",
        "terraform": "terraform",
        "checkov": "checkov",
        "kube-bench": "kube-bench",
        "kube-hunter": "kube-hunter",
        "docker-bench-security": "docker-bench-security",
        "clair-scanner": "clair",
        "dockle": "dockle",
        "hadolint": "hadolint",
        "snyk": "snyk",
        
        # DarkWeb Araçları
        "onionsearch": "onionsearch",
        "tor": "tor",
        "torbrowser-launcher": "torbrowser-launcher",
        "darkdump": "darkdump",
        "onioff": "onioff",
        "torbot": "torbot",
        "onionscan": "onionscan",
        "onionshare": "onionshare",
        "ricochet": "ricochet",
        "zeronet": "zeronet",
        "freenet": "freenet",
        "i2prouter": "i2p",
        "gnunet": "gnunet",
        "lokinet": "lokinet",
        "yggdrasil": "yggdrasil",
        
        # Blockchain Araçları
        "myth": "mythril",
        "slither": "slither-analyzer",
        "echidna-test": "echidna",
        "manticore": "manticore",
        "oyente": "oyente",
        "octopus": "octopus",
        "solhint": "solhint",
        "surya": "surya",
        "ganache": "ganache",
        "truffle": "truffle",
        "hardhat": "hardhat",
        "forge": "foundry",
        "brownie": "brownie",
        "solidity-coverage": "solidity-coverage",
        "slitherin": "slitherin",
        
        # IoT Araçları
        "iotseeker": "iotseeker",
        "btlejack": "btlejack",
        "zbstumbler": "killerbee",
        "hackrf_transfer": "hackrf",
        "rsf.py": "routersploit",
        "pret": "pret",
        "iot-inspector": "iot-inspector",
        "ext-firmware": "firmware-mod-kit",
        "binwalk": "binwalk",
        "firmadyne": "firmadyne",
        "fat.py": "firmware-analysis-toolkit",
        "emba": "emba",
        "fact": "fact",
        "ofrak": "ofrak",
        "qiling": "qiling",
        "unicorn": "unicorn",
        "angr": "angr",
        "ghidra": "ghidra",
        "r2": "radare2",
        "gdb": "gdb",
        "pulseview": "pulseview",
        "flashrom": "flashrom",
        "openocd": "openocd",
        
        # Forensic Araçları
        "autopsy": "autopsy",
        "volatility": "volatility",
        "binwalk": "binwalk",
        "ghidra": "ghidra",
        "testdisk": "testdisk",
        "exiftool": "exiftool",
        "foremost": "foremost",
        "strings": "binutils",
        "bulk_extractor": "bulk-extractor",
        "steghide": "steghide",
        "stegsnow": "stegsnow",
        "zsteg": "zsteg",
        "outguess": "outguess",
        "clamscan": "clamav",
        "yara": "yara",
        "pescan": "pescan",
        "peid": "peid",
        "upx": "upx",
        "cuckoo": "cuckoo",
        "vt": "virustotal-cli",
        "wireshark": "wireshark",
        "tcpdump": "tcpdump",
        "tshark": "tshark",
        "networkminer": "networkminer",
        "xplico": "xplico",
    }
    
    @classmethod
    def check_tool(cls, tool_cmd: str) -> bool:
        """Aracın kurulu olup olmadığını kontrol eder."""
        if not tool_cmd:
            return False
        cmd = tool_cmd.split()[0]
        
        # Özel durumlar
        if cmd in ["airodump-ng", "aireplay-ng", "airmon-ng"]:
            result = subprocess.run("which aircrack-ng", shell=True, capture_output=True, text=True)
            return result.returncode == 0
        
        result = subprocess.run(f"which {cmd} 2>/dev/null", shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    @classmethod
    def get_package_name(cls, tool_cmd: str) -> str:
        """Araç komutundan paket adını bulur."""
        cmd = tool_cmd.split()[0] if tool_cmd else ""
        return cls.TOOL_PACKAGES.get(cmd, cmd)
    
    @classmethod
    def install_tool(cls, tool_cmd: str) -> tuple:
        """Aracı kurmayı dener. (başarı, mesaj) döner."""
        cmd_name = tool_cmd.split()[0] if tool_cmd else ""
        pkg = cls.TOOL_PACKAGES.get(cmd_name, cmd_name)
        
        if not pkg:
            return False, f"{cmd_name} için paket bulunamadı"
        
        try:
            # 1. APT ile dene
            result = subprocess.run(f"sudo apt install -y {pkg} 2>/dev/null", 
                                   shell=True, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                return True, f"{cmd_name} apt ile kuruldu"
            
            # 2. Snap ile dene
            result = subprocess.run(f"sudo snap install {pkg} 2>/dev/null", 
                                   shell=True, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                return True, f"{cmd_name} snap ile kuruldu"
            
            # 3. PIP3 ile dene
            result = subprocess.run(f"sudo pip3 install {pkg} --break-system-packages 2>/dev/null", 
                                   shell=True, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                return True, f"{cmd_name} pip3 ile kuruldu"
            
            # 4. Gem ile dene
            result = subprocess.run(f"sudo gem install {pkg} 2>/dev/null", 
                                   shell=True, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                return True, f"{cmd_name} gem ile kuruldu"
            
            # 5. Go ile dene
            result = subprocess.run(f"go install github.com/{pkg}@latest 2>/dev/null", 
                                   shell=True, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                return True, f"{cmd_name} go ile kuruldu"
            
            return False, f"{cmd_name} kurulamadı (tüm yöntemler başarısız)"
            
        except subprocess.TimeoutExpired:
            return False, f"{cmd_name} kurulum zaman aşımı"
        except Exception as e:
            return False, f"{cmd_name} kurulum hatası: {str(e)}"
    
    @classmethod
    def install_batch(cls, tool_list: List[str], callback=None) -> Dict:
        """Birden fazla aracı toplu kurar."""
        results = {}
        total = len(tool_list)
        
        for i, tool in enumerate(tool_list):
            if callback:
                callback(f"Kuruluyor ({i+1}/{total}): {tool}")
            
            success, message = cls.install_tool(tool)
            results[tool] = {"success": success, "message": message}
            
            if callback:
                callback(f"  {'✓' if success else '✗'} {message}")
        
        return results
    
    @classmethod
    def get_missing_tools(cls, tools: Dict[int, any]) -> List[str]:
        """Bir araç sözlüğünden eksik olanları döner."""
        missing = []
        for tool_id, tool in tools.items():
            if hasattr(tool, 'command'):
                cmd = tool.command.split()[0] if tool.command else ""
                if cmd and not cls.check_tool(cmd):
                    missing.append(cmd)
        return list(set(missing))
    
    @classmethod
    def get_installed_tools(cls, tools: Dict[int, any]) -> List[str]:
        """Bir araç sözlüğünden kurulu olanları döner."""
        installed = []
        for tool_id, tool in tools.items():
            if hasattr(tool, 'command'):
                cmd = tool.command.split()[0] if tool.command else ""
                if cmd and cls.check_tool(cmd):
                    installed.append(cmd)
        return list(set(installed))
