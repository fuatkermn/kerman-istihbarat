#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import webbrowser

class ReportGenerator:
    def __init__(self, db=None):
        self.db = db
        self.report_dir = Path.home() / "kerman_reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html(self, operations: List[Dict], findings: List[Dict], title: str = "KERMAN İSTİHBARAT RAPORU") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.report_dir / f"rapor_{timestamp}.html"
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ background: #0a0a0a; color: #00ff00; font-family: monospace; padding: 20px; }}
        h1 {{ color: red; text-align: center; border-bottom: 2px solid #00ff00; padding-bottom: 10px; }}
        h2 {{ color: #00cc00; }}
        .section {{ border: 1px solid #00ff00; margin: 20px 0; padding: 15px; }}
        .operation {{ background: #111; margin: 10px 0; padding: 10px; border-left: 3px solid #00ff00; }}
        .finding {{ background: #1a0000; margin: 10px 0; padding: 10px; border-left: 3px solid red; }}
        .success {{ color: #00ff00; }}
        .failed {{ color: red; }}
        .critical {{ color: #ff0000; font-weight: bold; }}
        .high {{ color: #ff6600; }}
        .medium {{ color: #ffcc00; }}
        .low {{ color: #00ccff; }}
        pre {{ background: #000; padding: 10px; overflow-x: auto; white-space: pre-wrap; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat {{ text-align: center; padding: 10px; background: #111; border: 1px solid #00ff00; }}
        .stat-value {{ font-size: 24px; font-weight: bold; }}
        .stat-label {{ color: #888; }}
    </style>
</head>
<body>
    <h1>⚡ {title} ⚡</h1>
    <p class="timestamp">Oluşturulma: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
    
    <div class="summary">
        <div class="stat">
            <div class="stat-value">{len(operations)}</div>
            <div class="stat-label">İşlem</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(findings)}</div>
            <div class="stat-label">Bulgu</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📋 Yapılan İşlemler</h2>
"""
        
        for op in operations:
            status_class = "success" if op.get('status') == 'SUCCESS' else "failed"
            html += f"""
        <div class="operation">
            <strong>{op.get('tool_name', 'Bilinmeyen')}</strong> 
            <span class="{status_class}">[{op.get('status', '?')}]</span>
            <br>
            <small>Komut: {op.get('command', '')}</small>
            <br>
            <small class="timestamp">{op.get('created_at', '')}</small>
        </div>
"""
        
        html += """
    </div>
    
    <div class="section">
        <h2>🔍 Tespit Edilen Bulgular</h2>
"""
        
        severity_map = {"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low"}
        for f in findings:
            sev = f.get('severity', 'INFO').upper()
            sev_class = severity_map.get(sev, "low")
            html += f"""
        <div class="finding">
            <strong class="{sev_class}">[{sev}] {f.get('title', 'Başlıksız')}</strong>
            <p>{f.get('description', '')}</p>
"""
            if f.get('cve'):
                html += f"<small>CVE: {f.get('cve')}</small><br>"
            if f.get('cvss'):
                html += f"<small>CVSS: {f.get('cvss')}</small><br>"
            if f.get('remediation'):
                html += f"<p><strong>Çözüm:</strong> {f.get('remediation')}</p>"
            html += f'<small class="timestamp">{f.get("created_at", "")}</small>\n        </div>\n'
        
        html += """
    </div>
    
    <footer style="text-align: center; margin-top: 30px; color: #666;">
        KERMAN İSTİHBARAT v2.0.0 | Otomatik Oluşturuldu
    </footer>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        if self.db:
            self.db.add_report(title, "HTML", str(filename))
        
        return str(filename)
    
    def open_report(self, filepath: str):
        webbrowser.open(f"file://{filepath}")
