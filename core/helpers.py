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
