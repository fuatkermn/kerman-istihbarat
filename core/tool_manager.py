# WiFi Araçları
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

# OSINT Araçları
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

# Web Araçları
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

# Exploit Araçları
exploit_tools = [
    Tool(31, "Metasploit - Sızma Çerçevesi", "Exploit", "msfconsole -q", "Metasploit Framework", True),
    Tool(32, "SearchSploit - Açıklık Arama", "Exploit", "searchsploit {target}", "Exploit-DB araması"),
    Tool(33, "Hydra - Kaba Kuvvet", "Exploit", "hydra -l {user} -P {wordlist} {target} {service}", "Parola deneme", True),
    Tool(34, "John - Parola Kırma", "Exploit", "john --wordlist={wordlist} {hash}", "John the Ripper"),
    Tool(35, "Hashcat - GPU Parola Kırma", "Exploit", "hashcat -m 0 {hash} {wordlist}", "GPU destekli kırma"),
]
