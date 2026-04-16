#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess

@dataclass
class Tool:
    tool_id: int
    name: str
    category: str
    command: str
    description: str = ""
    requires_root: bool = False

class ToolManager:
    def __init__(self):
        self.tools: Dict[int, Tool] = {}
        self.categories: Dict[str, List[int]] = {}
        self.current_process = None
        self._load_builtin_tools()
    
    def _load_builtin_tools(self):
        # WiFi (1-25)
        wifi_tools = [
            Tool(1, "Airodump-ng - Kablosuz Ağ Tarama", "WiFi", "airodump-ng {interface}", "Kablosuz ağları tarar", True),
            Tool(2, "Aireplay-ng - Bağlantı Kesme", "WiFi", "aireplay-ng -0 0 -a {bssid} {interface}", "Deauth saldırısı", True),
            Tool(3, "Wifite - Otomatik Saldırı", "WiFi", "wifite --kill", "Otomatik WiFi saldırısı", True),
            Tool(4, "Bettercap - Ağ Keşfi", "WiFi", "bettercap -eval 'wifi.recon on'", "Bettercap WiFi keşif", True),
            Tool(5, "MDK4 - Beacon Flood", "WiFi", "mdk4 {interface} b -s 500", "Sahte ağ oluşturma", True),
            Tool(6, "Reaver - WPS Kırma", "WiFi", "reaver -i {interface} -b {bssid} -vv", "WPS PIN kırma", True),
            Tool(7, "Kismet - Pasif Keşif", "WiFi", "kismet -c {interface}", "Pasif WiFi keşif", True),
            Tool(8, "Airgeddon - WiFi Çerçevesi", "WiFi", "airgeddon", "Çok amaçlı WiFi aracı", True),
            Tool(9, "Wash - WPS Ağ Tarama", "WiFi", "wash -i {interface}", "WPS etkin ağları bulur", True),
            Tool(10, "HCXDumpTool - Paket Yakalama", "WiFi", "hcxdumptool -i {interface} -o capture.pcapng", "WPA paket yakalama", True),
            Tool(11, "Aircrack-ng - WPA Kırma", "WiFi", "aircrack-ng -w {wordlist} -b {bssid} {capture}", "WPA parola kırma", True),
            Tool(12, "Pyrit - GPU Kırma", "WiFi", "pyrit -r {capture} -i {wordlist} attack_passthrough", "GPU destekli WPA kırma", True),
            Tool(13, "Cowpatty - WPA Kırma", "WiFi", "cowpatty -r {capture} -f {wordlist} -s {essid}", "WPA PSK kırma", True),
            Tool(14, "EAPHammer - Enterprise WiFi", "WiFi", "eaphammer -i {interface} --auth wpa-eap --essid {target}", "Enterprise WiFi saldırısı", True),
            Tool(15, "Wifipumpkin3 - Sahte AP", "WiFi", "wifipumpkin3", "Sahte erişim noktası", True),
            Tool(16, "Fluxion - Sosyal Mühendislik", "WiFi", "fluxion", "Sahte login sayfası", True),
            Tool(17, "Linset - Evil Twin", "WiFi", "linset", "Evil Twin saldırısı", True),
            Tool(18, "WPSPin - WPS PIN Üretici", "WiFi", "wpspin {bssid}", "WPS PIN hesaplama", True),
            Tool(19, "Pixiewps - WPS Kırma", "WiFi", "pixiewps", "Pixie Dust saldırısı", True),
            Tool(20, "Airssl - SSL Saldırı", "WiFi", "airssl {interface}", "SSL strip saldırısı", True),
            Tool(21, "Airjack - Paket Enjeksiyon", "WiFi", "airjack -i {interface}", "Paket enjeksiyon", True),
            Tool(22, "WEPbuster - WEP Kırma", "WiFi", "wepbuster -i {interface}", "WEP şifre kırma", True),
            Tool(23, "Fern WiFi Cracker", "WiFi", "fern-wifi-cracker", "GUI WiFi kırma aracı", True),
            Tool(24, "Ghost Phisher", "WiFi", "ghost-phisher", "Sahte AP ve phishing", True),
            Tool(25, "WiFi Honey", "WiFi", "wifi-honey", "Honeypot AP", True),
        ]
        for t in wifi_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("WiFi", []).append(t.tool_id)
        
        # OSINT (26-60)
        osint_tools = [
            Tool(26, "Nmap - Hızlı Tarama", "OSINT", "nmap -T4 -F {target}", "Hızlı port taraması"),
            Tool(27, "Nmap - Ayrıntılı Tarama", "OSINT", "nmap -sV -sC -O {target}", "Detaylı servis taraması"),
            Tool(28, "Sherlock - Kullanıcı Adı Arama", "OSINT", "sherlock {target}", "Sosyal medya taraması"),
            Tool(29, "TheHarvester - E-posta/Domain", "OSINT", "theHarvester -d {domain} -b all", "E-posta adresi toplama"),
            Tool(30, "Amass - Alt Domain Keşfi", "OSINT", "amass enum -d {domain}", "Subdomain keşfi"),
            Tool(31, "Subfinder - Alt Domain Bulma", "OSINT", "subfinder -d {domain}", "Hızlı subdomain tarama"),
            Tool(32, "Holehe - E-posta Denetimi", "OSINT", "holehe {target}", "E-posta hesap kontrolü"),
            Tool(33, "Maigret - Sosyal Medya Tarama", "OSINT", "maigret {target}", "Kullanıcı adı sorgulama"),
            Tool(34, "Recon-ng - Web Keşif", "OSINT", "recon-ng", "Web tabanlı keşif"),
            Tool(35, "Whois - Domain Sorgulama", "OSINT", "whois {domain}", "Domain bilgileri"),
            Tool(36, "Shodan - IoT Arama", "OSINT", "shodan search {query}", "Shodan arama motoru"),
            Tool(37, "Censys - Internet Tarama", "OSINT", "censys search {query}", "Censys araması"),
            Tool(38, "SpiderFoot - Otomatik OSINT", "OSINT", "spiderfoot -s {target}", "Otomatik istihbarat"),
            Tool(39, "Maltego CE", "OSINT", "maltego", "Grafik tabanlı OSINT"),
            Tool(40, "Photon - Web Crawler", "OSINT", "photon -u {target}", "Web kazıyıcı"),
            Tool(41, "TruffleHog - Git Sızıntısı", "OSINT", "trufflehog {target}", "Git repo sızıntı tarama"),
            Tool(42, "GitRob - GitHub Tarama", "OSINT", "gitrob {target}", "GitHub hassas veri"),
            Tool(43, "Twint - Twitter Kazıma", "OSINT", "twint -u {target}", "Twitter veri çekme"),
            Tool(44, "Instaloader - Instagram", "OSINT", "instaloader {target}", "Instagram indirici"),
            Tool(45, "ExifTool - Meta Veri", "OSINT", "exiftool {file}", "Dosya meta analizi"),
            Tool(46, "Metagoofil - Belge Meta", "OSINT", "metagoofil -d {domain} -t pdf,doc", "Belge meta veri"),
            Tool(47, "Tinfoleak - Twitter Analiz", "OSINT", "tinfoleak -u {target}", "Twitter hesap analizi"),
            Tool(48, "Osintgram - Instagram OSINT", "OSINT", "osintgram {target}", "Instagram istihbarat"),
            Tool(49, "Social-analyzer - Profil Analiz", "OSINT", "social-analyzer --username {target}", "Sosyal medya analizi"),
            Tool(50, "Dmitry - Deepmagic", "OSINT", "dmitry -i -e {target}", "Temel bilgi toplama"),
            Tool(51, "Masscan - Toplu Tarama", "OSINT", "masscan -p1-65535 {target}", "Hızlı port tarama"),
            Tool(52, "RustScan - Hızlı Tarama", "OSINT", "rustscan -a {target}", "3 saniyede port tarama"),
            Tool(53, "AutoRecon - Otomatik Keşif", "OSINT", "autorecon {target}", "Otomatik servis keşfi"),
            Tool(54, "Sparta - Ağ Pentest", "OSINT", "sparta", "GUI pentest aracı"),
            Tool(55, "Legion - Pentest Framework", "OSINT", "legion", "Sparta fork pentest"),
            Tool(56, "Faraday - İşbirlikçi Pentest", "OSINT", "faraday", "Takım pentest IDE"),
            Tool(57, "Armitage - Metasploit GUI", "OSINT", "armitage", "Metasploit GUI"),
            Tool(58, "LittleBrother - Kullanıcı Takibi", "OSINT", "littlebrother {target}", "Dijital ayak izi"),
            Tool(59, "YouTube-DL - Video İndir", "OSINT", "youtube-dl {target}", "YouTube indirici"),
            Tool(60, "FOCA - Meta Veri Analizi", "OSINT", "foca", "Windows meta analizi"),
        ]
        for t in osint_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("OSINT", []).append(t.tool_id)
        
        # Web (61-100)
        web_tools = [
            Tool(61, "SQLMap - SQL Enjeksiyon", "Web", "sqlmap -u {target} --batch --dbs", "Otomatik SQL injection"),
            Tool(62, "Gobuster - Dizin Tarama", "Web", "gobuster dir -u {target} -w {wordlist}", "Dizin keşfi"),
            Tool(63, "FFUF - Web Fuzzing", "Web", "ffuf -u {target}/FUZZ -w {wordlist}", "Hızlı web fuzzer"),
            Tool(64, "WPScan - WordPress Tarama", "Web", "wpscan --url {target}", "WordPress güvenlik taraması"),
            Tool(65, "Nikto - Web Sunucu Tarama", "Web", "nikto -h {target}", "Web sunucu açıklıkları"),
            Tool(66, "Nuclei - Zafiyet Tarayıcı", "Web", "nuclei -u {target}", "Şablon tabanlı tarama"),
            Tool(67, "XSStrike - XSS Tarayıcı", "Web", "xsstrike -u {target}", "Gelişmiş XSS tespiti"),
            Tool(68, "Dirb - Dizin Keşfi", "Web", "dirb {target} {wordlist}", "Klasik dizin tarama"),
            Tool(69, "WhatWeb - Teknoloji Tanıma", "Web", "whatweb {target}", "Web teknolojilerini tanır"),
            Tool(70, "Commix - Komut Enjeksiyon", "Web", "commix --url {target}", "Command injection testi"),
            Tool(71, "Burp Suite", "Web", "burpsuite", "Web güvenlik testi"),
            Tool(72, "OWASP ZAP", "Web", "zaproxy", "OWASP ZAP proxy"),
            Tool(73, "Skipfish - Web Tarayıcı", "Web", "skipfish -o output {target}", "Aktif web tarayıcı"),
            Tool(74, "Wapiti - Web Tarayıcı", "Web", "wapiti -u {target}", "Web zafiyet tarayıcı"),
            Tool(75, "Vega - Web Tarayıcı", "Web", "vega", "GUI web tarayıcı"),
            Tool(76, "Arachni - Web Tarayıcı", "Web", "arachni {target}", "Web güvenlik tarayıcı"),
            Tool(77, "Wfuzz - Web Fuzzer", "Web", "wfuzz -c -z file,{wordlist} {target}/FUZZ", "Web fuzzing aracı"),
            Tool(78, "Dirbuster - Dizin Tarama", "Web", "dirbuster -u {target}", "GUI dizin tarama"),
            Tool(79, "JoomScan - Joomla Tarama", "Web", "joomscan -u {target}", "Joomla tarayıcı"),
            Tool(80, "Droopescan - CMS Tarama", "Web", "droopescan scan drupal -u {target}", "Drupal tarayıcı"),
            Tool(81, "CMSmap - CMS Tarama", "Web", "cmsmap {target}", "CMS exploit tarayıcı"),
            Tool(82, "Magento Tarayıcı", "Web", "magescan {target}", "Magento tarayıcı"),
            Tool(83, "Dalfox - XSS Tarayıcı", "Web", "dalfox url {target}", "Hızlı XSS tarayıcı"),
            Tool(84, "XSpear - XSS Tarayıcı", "Web", "xspear -u {target}", "Ruby XSS tarayıcı"),
            Tool(85, "OpenRedirect - Açık Yönlendirme", "Web", "openredirect -u {target}", "Open redirect tarayıcı"),
            Tool(86, "CRLFuzz - CRLF Tarama", "Web", "crlfuzz -u {target}", "CRLF injection"),
            Tool(87, "SSRFmap - SSRF Test", "Web", "ssrfmap -r {target}", "SSRF exploit"),
            Tool(88, "XXEinjector - XXE Test", "Web", "xxeinjector {target}", "XXE enjeksiyon"),
            Tool(89, "LFISuite - LFI Test", "Web", "lfisuite -u {target}", "LFI exploit"),
            Tool(90, "NoSQLMap - NoSQL Enjeksiyon", "Web", "nosqlmap -u {target}", "NoSQL injection"),
            Tool(91, "GraphQLmap - GraphQL Test", "Web", "graphqlmap -u {target}", "GraphQL injection"),
            Tool(92, "SSTImap - SSTI Test", "Web", "sstimap -u {target}", "SSTI exploit"),
            Tool(93, "JWT Tool - JWT Kırma", "Web", "jwt_tool {target}", "JWT token analizi"),
            Tool(94, "Corsy - CORS Tarama", "Web", "corsy -u {target}", "CORS misconfig"),
            Tool(95, "Arjun - Parametre Keşfi", "Web", "arjun -u {target}", "HTTP parametre keşfi"),
            Tool(96, "ParamSpider - Parametre", "Web", "paramspider -d {domain}", "Domain'den parametre bul"),
            Tool(97, "LinkFinder - JS Analiz", "Web", "linkfinder -i {target} -o cli", "JS'den link bul"),
            Tool(98, "SecretFinder - JS Sızıntı", "Web", "secretfinder -i {target} -o cli", "JS'den secret bul"),
            Tool(99, "Subjack - Subdomain Takeover", "Web", "subjack -d {domain}", "Subdomain takeover"),
            Tool(100, "Aquatone - Ekran Görüntüsü", "Web", "aquatone -d {domain}", "Subdomain görselleştirme"),
        ]
        for t in web_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Web", []).append(t.tool_id)

        # Exploit (101-150)
        exploit_tools = [
            Tool(101, "Metasploit - Sızma Çerçevesi", "Exploit", "msfconsole -q", "Metasploit Framework", True),
            Tool(102, "SearchSploit - Açıklık Arama", "Exploit", "searchsploit {target}", "Exploit-DB araması"),
            Tool(103, "Hydra - Kaba Kuvvet", "Exploit", "hydra -l {user} -P {wordlist} {target} {service}", "Parola deneme"),
            Tool(104, "John - Parola Kırma", "Exploit", "john --wordlist={wordlist} {hash}", "John the Ripper"),
            Tool(105, "Hashcat - GPU Parola Kırma", "Exploit", "hashcat -m 0 {hash} {wordlist}", "GPU destekli kırma"),
            Tool(106, "BeEF - Tarayıcı Exploit", "Exploit", "beef-xss", "Browser Exploitation"),
            Tool(107, "Responder - LLMNR Poison", "Exploit", "responder -I {interface}", "NetBIOS zehirleme", True),
            Tool(108, "CrackMapExec - AD Saldırı", "Exploit", "crackmapexec smb {target}", "SMB saldırıları"),
            Tool(109, "SET - Sosyal Mühendislik", "Exploit", "setoolkit", "Social Engineer Toolkit"),
            Tool(110, "Empire - Post-Exploit", "Exploit", "empire", "PowerShell post-exploit"),
            Tool(111, "Mimikatz - Credential Dump", "Exploit", "mimikatz", "Windows kimlik bilgileri"),
            Tool(112, "LaZagne - Parola Toplama", "Exploit", "lazagne all", "Tüm parolaları toplar"),
            Tool(113, "PowerSploit - PowerShell", "Exploit", "powersploit", "PowerShell exploit"),
            Tool(114, "Nishang - PowerShell", "Exploit", "nishang", "PowerShell pentest"),
            Tool(115, "Veil - AV Atlatma", "Exploit", "veil", "Payload şifreleme"),
            Tool(116, "Shellter - AV Atlatma", "Exploit", "shellter", "Dinamik payload"),
            Tool(117, "Msfvenom - Payload Üret", "Exploit", "msfvenom -p windows/meterpreter/reverse_tcp LHOST={target} LPORT={port} -f exe", "Payload üretici"),
            Tool(118, "RouterSploit - Router Exploit", "Exploit", "rsf.py", "Gömülü cihaz exploit"),
            Tool(119, "Linux Exploit Suggester", "Exploit", "linux-exploit-suggester", "Linux exploit önerici"),
            Tool(120, "Windows Exploit Suggester", "Exploit", "windows-exploit-suggester", "Windows exploit"),
            Tool(121, "LinPEAS - Linux PE", "Exploit", "linpeas", "Linux yetki yükseltme"),
            Tool(122, "WinPEAS - Windows PE", "Exploit", "winpeas", "Windows yetki yükseltme"),
            Tool(123, "Chisel - Tünelleme", "Exploit", "chisel server --port {port}", "TCP tünelleme"),
            Tool(124, "Ngrok - Tünelleme", "Exploit", "ngrok tcp {port}", "Public tünelleme"),
            Tool(125, "Socat - Port Yönlendirme", "Exploit", "socat TCP-LISTEN:{port},fork TCP:{target}:{port}", "Port yönlendirme"),
            Tool(126, "Netcat - İsviçre Çakısı", "Exploit", "nc -lvnp {port}", "Netcat dinleyici"),
            Tool(127, "Ncat - Gelişmiş Netcat", "Exploit", "ncat -lvnp {port} --ssl", "SSL Netcat"),
            Tool(128, "BruteSpray - Toplu Brute", "Exploit", "brutespray -f nmap.xml", "Nmap'ten brute force"),
            Tool(129, "Crowbar - RDP Brute", "Exploit", "crowbar -b rdp -s {target} -u {user} -C {wordlist}", "RDP brute force"),
            Tool(130, "Medusa - Paralel Brute", "Exploit", "medusa -h {target} -u {user} -P {wordlist} -M {service}", "Hızlı brute force"),
            Tool(131, "Privilege Escalation Awesome Scripts", "Exploit", "peass-ng", "PEASS-ng suite"),
            Tool(132, "GTFOBins Lookup", "Exploit", "gtfobins {target}", "SUID/Sudo exploit"),
            Tool(133, "LOLBAS Lookup", "Exploit", "lolbas {target}", "Windows LOLBin"),
            Tool(134, "PwnKit - Polkit Exploit", "Exploit", "pwnkit", "CVE-2021-4034"),
            Tool(135, "DirtyPipe - Linux Exploit", "Exploit", "dirtypipe", "CVE-2022-0847"),
            Tool(136, "Log4j Scanner", "Exploit", "log4j-scan {target}", "Log4Shell tarayıcı"),
            Tool(137, "Spring4Shell Scanner", "Exploit", "spring4shell-scan {target}", "Spring4Shell"),
            Tool(138, "Heartbleed Scanner", "Exploit", "heartbleed {target}", "OpenSSL Heartbleed"),
            Tool(139, "Shellshock Scanner", "Exploit", "shellshock-scan {target}", "Shellshock tarama"),
            Tool(140, "EternalBlue Scanner", "Exploit", "eternalblue-scan {target}", "MS17-010 tarama"),
            Tool(141, "BlueKeep Scanner", "Exploit", "bluekeep-scan {target}", "CVE-2019-0708"),
            Tool(142, "SMBGhost Scanner", "Exploit", "smbghost-scan {target}", "CVE-2020-0796"),
            Tool(143, "Zerologon Scanner", "Exploit", "zerologon-scan {target}", "CVE-2020-1472"),
            Tool(144, "PrintNightmare Scanner", "Exploit", "printnightmare-scan", "CVE-2021-34527"),
            Tool(145, "HiveNightmare Scanner", "Exploit", "hivenightmare", "CVE-2021-36934"),
            Tool(146, "Sam the Admin", "Exploit", "sam-the-admin", "CVE-2021-42278/42287"),
            Tool(147, "NoPac Scanner", "Exploit", "nopac {target}", "CVE-2021-42278"),
            Tool(148, "PetitPotam Scanner", "Exploit", "petitpotam", "CVE-2021-36942"),
            Tool(149, "DFSCoerce Scanner", "Exploit", "dfscoerce", "DFS coercion"),
            Tool(150, "ShadowCoerce Scanner", "Exploit", "shadowcoerce", "Shadow coercion"),
        ]
        for t in exploit_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Exploit", []).append(t.tool_id)

        # Active Directory (151-180)
        ad_tools = [
            Tool(151, "BloodHound - AD Keşif", "AD", "bloodhound-python -d {domain} -u {user} -p {password} -c All", "AD haritalama"),
            Tool(152, "Evil-WinRM - Uzak Kabuk", "AD", "evil-winrm -i {target} -u {user} -p {password}", "WinRM shell"),
            Tool(153, "Impacket-secretsdump", "AD", "secretsdump.py {domain}/{user}:{password}@{target}", "Hash dökme"),
            Tool(154, "Impacket-psexec", "AD", "psexec.py {domain}/{user}:{password}@{target}", "Uzaktan komut"),
            Tool(155, "Kerberoast", "AD", "GetUserSPNs.py {domain}/{user}:{password} -request", "Kerberoasting"),
            Tool(156, "ASREPRoast", "AD", "GetNPUsers.py {domain}/{user} -no-pass", "AS-REP roasting"),
            Tool(157, "Rubeus", "AD", "Rubeus.exe kerberoast", "Kerberoasting aracı"),
            Tool(158, "Mimikatz - AD", "AD", "mimikatz.exe \"privilege::debug\" \"sekurlsa::logonpasswords\"", "Kimlik bilgileri"),
            Tool(159, "PowerView", "AD", "powerview", "AD keşif PowerShell"),
            Tool(160, "ADRecon", "AD", "adrecon", "AD bilgi toplama"),
            Tool(161, "ADExplorer", "AD", "adexplorer", "AD tarayıcı"),
            Tool(162, "Ldapdomaindump", "AD", "ldapdomaindump {target}", "LDAP bilgi dökme"),
            Tool(163, "Enum4linux", "AD", "enum4linux {target}", "SMB/CIFS bilgi"),
            Tool(164, "SMBClient", "AD", "smbclient -L {target}", "SMB paylaşım listeleme"),
            Tool(165, "SMBMap", "AD", "smbmap -H {target}", "SMB paylaşım tarama"),
            Tool(166, "RPCClient", "AD", "rpcclient -U \"\" {target}", "RPC bağlantısı"),
            Tool(167, "NetExec", "AD", "netexec smb {target}", "CrackMapExec fork"),
            Tool(168, "Certipy - ADCS Saldırı", "AD", "certipy find -u {user} -p {password} -dc-ip {target}", "ADCS saldırıları"),
            Tool(169, "PKINITtools", "AD", "gettgtpkinit.py {domain}/{user} -cert-pfx {cert}", "PKINIT saldırısı"),
            Tool(170, "PassTheCert", "AD", "passthecert.py", "Sertifika tabanlı auth"),
            Tool(171, "Coercer", "AD", "coercer", "Zorla kimlik doğrulama"),
            Tool(172, "MITM6", "AD", "mitm6 -d {domain}", "IPv6 DNS zehirleme"),
            Tool(173, "Responder - AD", "AD", "responder -I {interface} -A", "LLMNR/NBT-NS zehirleme"),
            Tool(174, "Inveigh", "AD", "inveigh", "PowerShell zehirleme"),
            Tool(175, "NTLMRelayX", "AD", "ntlmrelayx.py -tf targets.txt", "NTLM relay"),
            Tool(176, "PetitPotam", "AD", "petitpotam.py {attacker} {target}", "Zorla NTLM auth"),
            Tool(177, "PrinterBug", "AD", "printerbug.py {domain}/{user}:{password}@{target} {attacker}", "MS-RPRN coercion"),
            Tool(178, "DFSCoerce", "AD", "dfscoerce.py -d {domain} -u {user} -p {password} {target} {attacker}", "DFS coercion"),
            Tool(179, "ShadowCoerce", "AD", "shadowcoerce.py -d {domain} -u {user} -p {password} {target} {attacker}", "MS-FSRVP"),
            Tool(180, "RBCD Attack", "AD", "rbcd.py", "Resource-based constrained delegation"),
        ]
        for t in ad_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("AD", []).append(t.tool_id)

        # Cloud (181-200)
        cloud_tools = [
            Tool(181, "Trivy - Konteyner Tarama", "Cloud", "trivy image {docker_image}", "Docker imaj tarayıcı"),
            Tool(182, "Prowler - AWS Denetim", "Cloud", "prowler aws", "AWS güvenlik denetimi"),
            Tool(183, "ScoutSuite - Çoklu Bulut", "Cloud", "scout aws", "AWS/Azure/GCP"),
            Tool(184, "Kubescape - K8s Güvenlik", "Cloud", "kubescape scan", "Kubernetes tarama"),
            Tool(185, "TruffleHog - Gizli Anahtar", "Cloud", "trufflehog filesystem .", "Gizli anahtar tarayıcı"),
            Tool(186, "CloudSploit", "Cloud", "cloudsploit scan", "AWS/Azure/GCP güvenlik"),
            Tool(187, "CloudMapper", "Cloud", "cloudmapper", "AWS görselleştirme"),
            Tool(188, "Pacu - AWS Exploit", "Cloud", "pacu", "AWS exploit çerçevesi"),
            Tool(189, "AWS CLI", "Cloud", "aws s3 ls", "AWS komut satırı"),
            Tool(190, "GCloud CLI", "Cloud", "gcloud compute instances list", "Google Cloud CLI"),
            Tool(191, "Azure CLI", "Cloud", "az vm list", "Azure komut satırı"),
            Tool(192, "Terraform Validator", "Cloud", "terraform validate", "Terraform güvenlik"),
            Tool(193, "Checkov - IaC Tarama", "Cloud", "checkov -d .", "IaC güvenlik taraması"),
            Tool(194, "Kube-bench - K8s CIS", "Cloud", "kube-bench", "Kubernetes CIS benchmark"),
            Tool(195, "Kube-hunter - K8s Pentest", "Cloud", "kube-hunter", "Kubernetes pentest"),
            Tool(196, "Docker Bench Security", "Cloud", "docker-bench-security", "Docker CIS benchmark"),
            Tool(197, "Clair - Konteyner Tarama", "Cloud", "clair-scanner {docker_image}", "Konteyner zafiyet"),
            Tool(198, "Dockle - Dockerfile Lint", "Cloud", "dockle {docker_image}", "Dockerfile analizi"),
            Tool(199, "Hadolint - Dockerfile Lint", "Cloud", "hadolint Dockerfile", "Dockerfile linting"),
            Tool(200, "Snyk CLI", "Cloud", "snyk test", "Snyk güvenlik taraması"),
        ]
        for t in cloud_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Cloud", []).append(t.tool_id)

        # DarkWeb (201-215)
        darkweb_tools = [
            Tool(201, "OnionSearch - Onion Arama", "DarkWeb", "onionsearch {query}", "Dark web arama"),
            Tool(202, "Tor Browser", "DarkWeb", "torbrowser-launcher", "Tor tarayıcı"),
            Tool(203, "Ahmia - Onion Arama", "DarkWeb", "xdg-open https://ahmia.fi/search?q={query}", "Ahmia arama"),
            Tool(204, "DarkDump - Veri Sızıntısı", "DarkWeb", "darkdump --query {query}", "Dark web veri arama"),
            Tool(205, "Onioff - Onion Bağlantı", "DarkWeb", "onioff {target}", "Onion site kontrol"),
            Tool(206, "TorBot - Site Tarama", "DarkWeb", "torbot -u {target}", "Onion site tarayıcı"),
            Tool(207, "OnionScan - Güvenlik", "DarkWeb", "onionscan {target}", "Onion güvenlik"),
            Tool(208, "OnionShare - Dosya Paylaşım", "DarkWeb", "onionshare", "Anonim paylaşım"),
            Tool(209, "Ricochet - Anlık Mesaj", "DarkWeb", "ricochet", "Anonim mesajlaşma"),
            Tool(210, "ZeroNet", "DarkWeb", "zeronet", "Merkeziyetsiz web"),
            Tool(211, "Freenet", "DarkWeb", "freenet", "Anonim ağ"),
            Tool(212, "I2P", "DarkWeb", "i2prouter start", "I2P anonim ağ"),
            Tool(213, "GNUnet", "DarkWeb", "gnunet", "Anonim P2P"),
            Tool(214, "Lokinet", "DarkWeb", "lokinet", "Loki anonim ağ"),
            Tool(215, "Yggdrasil", "DarkWeb", "yggdrasil", "Mesh anonim ağ"),
        ]
        for t in darkweb_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("DarkWeb", []).append(t.tool_id)

        # Blockchain (216-235)
        blockchain_tools = [
            Tool(216, "Mythril - Akıllı Sözleşme", "Blockchain", "myth analyze {contract_addr}", "Ethereum analiz"),
            Tool(217, "Slither - Statik Analiz", "Blockchain", "slither {contract_addr}", "Solidity analiz"),
            Tool(218, "Echidna - Fuzzing", "Blockchain", "echidna-test {contract_addr}", "Fuzzing"),
            Tool(219, "Manticore - Sembolik", "Blockchain", "manticore {contract_addr}", "Sembolik yürütme"),
            Tool(220, "Oyente - Analiz", "Blockchain", "oyente -s {contract_addr}", "Ethereum analiz"),
            Tool(221, "Octopus - Analiz", "Blockchain", "octopus {contract_addr}", "Sözleşme analizi"),
            Tool(222, "Solhint - Linter", "Blockchain", "solhint {file}", "Solidity lint"),
            Tool(223, "Surya - Görselleştirme", "Blockchain", "surya graph {file}", "Sözleşme grafiği"),
            Tool(224, "NFT Tarayıcı", "Blockchain", "echo 'NFT analizi: https://opensea.io'", "NFT tespiti"),
            Tool(225, "Wallet Tarayıcı", "Blockchain", "echo 'Cüzdan: https://etherscan.io'", "Cüzdan kontrol"),
            Tool(226, "Ganache", "Blockchain", "ganache", "Test blockchain"),
            Tool(227, "Truffle", "Blockchain", "truffle", "Geliştirme çerçevesi"),
            Tool(228, "Hardhat", "Blockchain", "hardhat", "Geliştirme ortamı"),
            Tool(229, "Foundry", "Blockchain", "forge", "Solidity test"),
            Tool(230, "Brownie", "Blockchain", "brownie", "Python geliştirme"),
            Tool(231, "Web3.py", "Blockchain", "python3 -c \"from web3 import Web3\"", "Web3 kütüphanesi"),
            Tool(232, "Ethers.js", "Blockchain", "echo 'JavaScript Web3 kütüphanesi'", "Ethers.js"),
            Tool(233, "Metamask Snaps", "Blockchain", "echo 'Metamask Snap geliştirme'", "Snap geliştirme"),
            Tool(234, "Solidity Coverage", "Blockchain", "solidity-coverage", "Kod kapsama"),
            Tool(235, "Slitherin", "Blockchain", "slitherin", "Güvenlik analizi"),
        ]
        for t in blockchain_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Blockchain", []).append(t.tool_id)

        # IoT (236-260)
        iot_tools = [
            Tool(236, "IoTSeeker - Keşif", "IoT", "iotseeker {target}", "IoT cihaz keşfi"),
            Tool(237, "BTLEJack - BLE Saldırı", "IoT", "btlejack -d /dev/ttyACM0", "BLE saldırı"),
            Tool(238, "KillerBee - ZigBee", "IoT", "zbstumbler -c {channel}", "ZigBee tarama"),
            Tool(239, "HackRF - SDR", "IoT", "hackrf_transfer -r capture.iq", "Sinyal yakalama"),
            Tool(240, "Routersploit", "IoT", "rsf.py", "Router exploit"),
            Tool(241, "PRET - Yazıcı", "IoT", "pret {target} pjl", "Yazıcı exploit"),
            Tool(242, "IoT Inspector", "IoT", "iot-inspector", "Ağ trafiği analizi"),
            Tool(243, "Firmware Mod Kit", "IoT", "ext-firmware {file}", "Firmware analizi"),
            Tool(244, "Binwalk - Firmware", "IoT", "binwalk {file}", "Firmware çıkarma"),
            Tool(245, "Firmadyne", "IoT", "firmadyne", "Firmware emülasyon"),
            Tool(246, "FAT - Firmware Test", "IoT", "fat.py", "Firmware analiz"),
            Tool(247, "EMBA", "IoT", "emba", "Gömülü analiz"),
            Tool(248, "FACT", "IoT", "fact", "Firmware analiz"),
            Tool(249, "OFRAK", "IoT", "ofrak", "Firmware tersine"),
            Tool(250, "Qiling", "IoT", "qiling", "Emülasyon çerçevesi"),
            Tool(251, "Unicorn", "IoT", "unicorn", "CPU emülatör"),
            Tool(252, "Angr", "IoT", "angr", "Binary analiz"),
            Tool(253, "Ghidra - IoT", "IoT", "ghidra", "Tersine mühendislik"),
            Tool(254, "Radare2", "IoT", "r2 {file}", "Binary analiz"),
            Tool(255, "GDB", "IoT", "gdb {file}", "Hata ayıklama"),
            Tool(256, "JTAGulator", "IoT", "echo 'JTAG pin bulma'", "JTAG keşif"),
            Tool(257, "Bus Pirate", "IoT", "echo 'Bus Pirate arayüzü'", "Donanım hacking"),
            Tool(258, "Logic Analyzer", "IoT", "pulseview", "Sinyal analizi"),
            Tool(259, "Flashrom", "IoT", "flashrom -r backup.bin", "Flash okuma/yazma"),
            Tool(260, "OpenOCD", "IoT", "openocd", "On-chip debug"),
        ]
        for t in iot_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("IoT", []).append(t.tool_id)

        # Forensic (261-285)
        forensic_tools = [
            Tool(261, "Autopsy - Adli Bilişim", "Forensic", "autopsy", "Disk imaj analizi"),
            Tool(262, "Volatility - Bellek", "Forensic", "volatility -f {image} imageinfo", "RAM analizi"),
            Tool(263, "Binwalk - Firmware", "Forensic", "binwalk {file}", "Firmware analizi"),
            Tool(264, "Ghidra - Tersine", "Forensic", "ghidra", "NSA aracı"),
            Tool(265, "TestDisk - Kurtarma", "Forensic", "testdisk {device}", "Disk kurtarma"),
            Tool(266, "ExifTool - Meta Veri", "Forensic", "exiftool {file}", "Meta veri"),
            Tool(267, "Foremost - Dosya Kurtarma", "Forensic", "foremost -i {image} -o output", "Silinmiş dosya"),
            Tool(268, "Strings - Metin Çıkarma", "Forensic", "strings {file}", "Binary metin"),
            Tool(269, "Bulk Extractor", "Forensic", "bulk_extractor {image} -o output", "E-posta/URL"),
            Tool(270, "Steghide - Steganografi", "Forensic", "steghide extract -sf {file}", "Gizli veri"),
            Tool(271, "Stegsnow", "Forensic", "stegsnow -C {file}", "Whitespace stego"),
            Tool(272, "Zsteg", "Forensic", "zsteg {file}", "PNG/BMP stego"),
            Tool(273, "Outguess", "Forensic", "outguess -r {file} output", "Stego çıkarma"),
            Tool(274, "ClamAV", "Forensic", "clamscan {file}", "Antivirüs tarama"),
            Tool(275, "YARA", "Forensic", "yara rules.yara {file}", "Malware tespiti"),
            Tool(276, "PEScan", "Forensic", "pescan {file}", "PE analizi"),
            Tool(277, "PEiD", "Forensic", "peid {file}", "Packer tespiti"),
            Tool(278, "UPX", "Forensic", "upx -d {file}", "UPX unpack"),
            Tool(279, "Cuckoo Sandbox", "Forensic", "cuckoo submit {file}", "Malware analizi"),
            Tool(280, "VirusTotal API", "Forensic", "vt scan file {file}", "VT taraması"),
            Tool(281, "Wireshark", "Forensic", "wireshark", "Ağ analizi"),
            Tool(282, "Tcpdump", "Forensic", "tcpdump -i {interface} -w capture.pcap", "Paket yakalama"),
            Tool(283, "Tshark", "Forensic", "tshark -r capture.pcap", "CLI Wireshark"),
            Tool(284, "NetworkMiner", "Forensic", "networkminer", "Ağ adli bilişim"),
            Tool(285, "Xplico", "Forensic", "xplico", "Ağ adli bilişim"),
        ]
        for t in forensic_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Forensic", []).append(t.tool_id)

        # Spyware (286-320)
        spyware_tools = [
            Tool(286, "QuasarRAT - Analiz", "Spyware", "echo 'GitHub: https://github.com/quasar/Quasar'", "Açık kaynak RAT"),
            Tool(287, "AsyncRAT - Analiz", "Spyware", "echo 'GitHub: AsyncRAT'", "C# RAT"),
            Tool(288, "VenomRAT - Analiz", "Spyware", "echo 'GitHub: VenomRAT'", "Venom RAT"),
            Tool(289, "PupyRAT - Analiz", "Spyware", "echo 'GitHub: n1nj4sec/pupy'", "Python RAT"),
            Tool(290, "CHAOS - Analiz", "Spyware", "echo 'GitHub: tiagorlampert/CHAOS'", "Go RAT"),
            Tool(291, "Merlin C2", "Spyware", "echo 'GitHub: Ne0nd0g/merlin'", "HTTP/2 C2"),
            Tool(292, "Covenant C2", "Spyware", "echo 'GitHub: cobbr/Covenant'", ".NET C2"),
            Tool(293, "EvilOSX", "Spyware", "echo 'GitHub: Marten4n6/EvilOSX'", "macOS RAT"),
            Tool(294, "Stitch", "Spyware", "echo 'GitHub: nathanlopez/Stitch'", "Python RAT"),
            Tool(295, "EggShell", "Spyware", "echo 'GitHub: neoneggplant/EggShell'", "iOS/macOS RAT"),
            Tool(296, "Empire - Spyware", "Spyware", "echo 'PowerShell Empire'", "Post-exploit"),
            Tool(297, "Cobalt Strike", "Spyware", "echo 'Ticari C2'", "Cobalt Strike"),
            Tool(298, "Meterpreter", "Spyware", "echo 'Metasploit payload'", "Meterpreter"),
            Tool(299, "PoshC2", "Spyware", "echo 'GitHub: nettitude/PoshC2'", "PowerShell C2"),
            Tool(300, "Koadic", "Spyware", "echo 'GitHub: zerosum0x0/koadic'", "COM C2"),
            Tool(301, "SILENTTRINITY", "Spyware", "echo 'GitHub: byt3bl33d3r/SILENTTRINITY'", "Python C2"),
            Tool(302, "Mythic", "Spyware", "echo 'GitHub: its-a-feature/Mythic'", "C2 framework"),
            Tool(303, "Apfell", "Spyware", "echo 'GitHub: its-a-feature/Apfell'", "macOS C2"),
            Tool(304, "C3", "Spyware", "echo 'GitHub: FSecureLABS/C3'", "Custom C2"),
            Tool(305, "HARS", "Spyware", "echo 'GitHub: redcanaryco/HARS'", "HTTP/S C2"),
            Tool(306, "Keylogger - Python", "Spyware", "echo 'pynput ile keylogger'", "Klavye dinleme"),
            Tool(307, "Screen Capture", "Spyware", "echo 'PIL ile ekran görüntüsü'", "Ekran yakalama"),
            Tool(308, "Webcam Capture", "Spyware", "echo 'OpenCV ile webcam'", "Kamera yakalama"),
            Tool(309, "Microphone Record", "Spyware", "echo 'pyaudio ile ses kaydı'", "Mikrofon kaydı"),
            Tool(310, "Clipboard Monitor", "Spyware", "echo 'pyperclip ile pano'", "Pano izleme"),
            Tool(311, "File Exfiltration", "Spyware", "echo 'Dosya sızdırma'", "Veri hırsızlığı"),
            Tool(312, "DNS Tunneling", "Spyware", "echo 'dnscat2'", "DNS tünelleme"),
            Tool(313, "ICMP Tunneling", "Spyware", "echo 'icmptunnel'", "ICMP tünelleme"),
            Tool(314, "HTTP Tunneling", "Spyware", "echo 'HTTP üzerinden C2'", "HTTP tünelleme"),
            Tool(315, "WebSocket C2", "Spyware", "echo 'WebSocket C2'", "WebSocket C2"),
            Tool(316, "Anti-VM Detection", "Spyware", "echo 'VM tespiti'", "Anti-VM"),
            Tool(317, "Anti-Debug", "Spyware", "echo 'Debug tespiti'", "Anti-debug"),
            Tool(318, "Persistence - Windows", "Spyware", "echo 'Registry run'", "Kalıcılık"),
            Tool(319, "Persistence - Linux", "Spyware", "echo 'crontab'", "Kalıcılık"),
            Tool(320, "Persistence - macOS", "Spyware", "echo 'LaunchAgent'", "Kalıcılık"),
        ]
        for t in spyware_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Spyware", []).append(t.tool_id)

        # Scenarios (321-350)
        scenarios_tools = [
            Tool(321, "WiFi WPA Kırma", "Scenarios", "echo 'WPA el sıkışma + aircrack'", "WPA senaryosu"),
            Tool(322, "SQL Injection", "Scenarios", "echo 'SQLMap ile veritabanı dökme'", "SQLi senaryosu"),
            Tool(323, "XSS Cookie Çalma", "Scenarios", "echo 'XSS ile cookie çalma'", "XSS senaryosu"),
            Tool(324, "AD Yetki Yükseltme", "Scenarios", "echo 'Kerberoasting + Pass-the-Hash'", "AD senaryosu"),
            Tool(325, "Docker Kaçış", "Scenarios", "echo 'docker run -v /:/host'", "Container escape"),
            Tool(326, "Dark Web OSINT", "Scenarios", "echo 'OnionSearch ile veri arama'", "Dark web"),
            Tool(327, "Akıllı Sözleşme Hack", "Scenarios", "echo 'Reentrancy açığı'", "Blockchain"),
            Tool(328, "Android Backdoor", "Scenarios", "echo 'msfvenom Android payload'", "Android RAT"),
            Tool(329, "RAT Analizi", "Scenarios", "echo 'strings malware.exe'", "Malware analizi"),
            Tool(330, "Sızma Testi Raporu", "Scenarios", "echo 'Tam pentest metodolojisi'", "Raporlama"),
            Tool(331, "Phishing Saldırısı", "Scenarios", "echo 'SET ile oltalama'", "Phishing"),
            Tool(332, "USB Rubber Ducky", "Scenarios", "echo 'Kötü amaçlı USB'", "USB saldırısı"),
            Tool(333, "Bluetooth Saldırısı", "Scenarios", "echo 'Blueborne exploit'", "Bluetooth"),
            Tool(334, "RFID Klonlama", "Scenarios", "echo 'Proxmark3 ile RFID'", "RFID"),
            Tool(335, "SDR Saldırısı", "Scenarios", "echo 'HackRF ile sinyal'", "SDR"),
            Tool(336, "VoIP Saldırısı", "Scenarios", "echo 'SIPVicious'", "VoIP"),
            Tool(337, "SCADA Saldırısı", "Scenarios", "echo 'Modbus saldırısı'", "SCADA"),
            Tool(338, "Kubernetes Saldırısı", "Scenarios", "echo 'Kube-hunter'", "K8s"),
            Tool(339, "AWS S3 Sızıntısı", "Scenarios", "echo 'AWS bucket tarama'", "Cloud"),
            Tool(340, "GCP Bucket Sızıntısı", "Scenarios", "echo 'GCP bucket'", "Cloud"),
            Tool(341, "Azure Blob Sızıntısı", "Scenarios", "echo 'Azure blob'", "Cloud"),
            Tool(342, "Log4j Exploit", "Scenarios", "echo 'Log4Shell exploit'", "Log4j"),
            Tool(343, "Spring4Shell Exploit", "Scenarios", "echo 'Spring4Shell'", "Spring"),
            Tool(344, "Heartbleed Exploit", "Scenarios", "echo 'OpenSSL Heartbleed'", "Heartbleed"),
            Tool(345, "Shellshock Exploit", "Scenarios", "echo 'Bash Shellshock'", "Shellshock"),
            Tool(346, "EternalBlue Exploit", "Scenarios", "echo 'MS17-010'", "EternalBlue"),
            Tool(347, "BlueKeep Exploit", "Scenarios", "echo 'CVE-2019-0708'", "BlueKeep"),
            Tool(348, "Zerologon Exploit", "Scenarios", "echo 'CVE-2020-1472'", "Zerologon"),
            Tool(349, "PrintNightmare", "Scenarios", "echo 'CVE-2021-34527'", "PrintNightmare"),
            Tool(350, "PetitPotam", "Scenarios", "echo 'CVE-2021-36942'", "PetitPotam"),
        ]
        for t in scenarios_tools:
            self.tools[t.tool_id] = t
            self.categories.setdefault("Scenarios", []).append(t.tool_id)

    def get_tool(self, tool_id: int) -> Optional[Tool]:
        return self.tools.get(tool_id)
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        ids = self.categories.get(category, [])
        return [self.tools[i] for i in ids if i in self.tools]
    
    def get_all_categories(self) -> List[str]:
        return list(self.categories.keys())
    
    def stop_current(self):
        if self.current_process:
            self.current_process.terminate()
    
       def run_tool(self, tool_id: int, params: Dict[str, str]) -> Dict:
        tool = self.get_tool(tool_id)
        if not tool:
            return {"error": f"Araç bulunamadı: {tool_id}"}
        
        cmd = tool.command
        
        # Parametreleri yerleştir
        for key, value in params.items():
            if value:
                cmd = cmd.replace(f"{{{key}}}", str(value))
        
        # Varsayılan değerleri temizle (yerleştirilmemiş olanları kaldır)
        import re
        cmd = re.sub(r'\{[^}]+\}', '', cmd)
        
        # Fazla boşlukları temizle
        cmd = ' '.join(cmd.split())
        
        # Eğer komut boşsa hata döndür
        if not cmd:
            return {"error": "Komut oluşturulamadı. Lütfen gerekli alanları doldurun."}
        
        print(f"[DEBUG] Çalıştırılıyor: {cmd}")
        
        try:
            # Komutu gerçekten çalıştır
            self.current_process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Çıktıyı satır satır oku (gerçek zamanlı için)
            stdout_lines = []
            stderr_lines = []
            
            try:
                stdout, stderr = self.current_process.communicate(timeout=300)
                stdout_lines = stdout.split('\n') if stdout else []
                stderr_lines = stderr.split('\n') if stderr else []
            except subprocess.TimeoutExpired:
                self.current_process.kill()
                stdout, stderr = self.current_process.communicate()
                return {"error": f"Zaman aşımı (300s). Kısmi çıktı:\n{stdout}"}
            
            return_code = self.current_process.returncode
            
            return {
                "tool": tool.name,
                "command": cmd,
                "return_code": return_code,
                "stdout": stdout if stdout else "",
                "stderr": stderr if stderr else "",
                "success": return_code == 0
            }
            
        except FileNotFoundError:
            return {"error": f"Komut bulunamadı: {cmd.split()[0]}. Lütfen aracın kurulu olduğundan emin olun."}
        except Exception as e:
            return {"error": f"Beklenmeyen hata: {str(e)}"}
