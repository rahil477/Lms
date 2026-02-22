#!/usr/bin/env python
"""
Simple solution: Use ngrok online tool without installation
Or use Python's built-in socketserver as a simple tunnel

Usage:
1. Visit https://ngrok.com/download
2. Download ngrok for Windows
3. Extract and run: ngrok http 8000

But if ngrok is not available, you can share your local IP with others:
- http://192.168.1.89:8000/az/

For external network access without installing anything:
- Use: https://serveo.net/
  Command: ssh -R 80:localhost:8000 serveo.net
  
- Or use: https://expose.dev/ (Laravel Valet)
  
- Or use Online ngrok: https://dashboard.ngrok.com/
"""

import subprocess
import sys
import webbrowser

def setup_tunnel():
    print(__doc__)
    
    # Option 1: Try ngrok if available
    try:
        print("\n" + "="*60)
        print("🌐 Starting ngrok tunnel...")
        print("="*60)
        result = subprocess.run(["ngrok", "http", "8000"], check=False)
        if result.returncode == 0:
            return
    except FileNotFoundError:
        print("❌ ngrok not found. Using alternative method...")
    
    # Option 2: Manual setup instruction
    print("\n" + "="*60)
    print("📋 EXTERNAL ACCESS SETUP")
    print("="*60)
    print("""
    Django Sunucunuz şu anda çalışıyor:
    
    ✅ Yerel Erişim (Aynı Wi-Fi):
       http://192.168.1.89:8000/az/
    
    ❌ Dış Ağ Erişimi İçin Seçenekler:
    
    1️⃣ ngrok Kullan (Tavsiye Edilen):
       a) https://ngrok.com/download adresinden indir
       b) Extract et
       c) Terminalinde çalıştır: ngrok http 8000
       d) Dış URL'yi al
    
    2️⃣ Serveo.net Kullan (SSH Gerekli):
       ssh -R 80:localhost:8000 serveo.net
    
    3️⃣ Port Forwarding (Router'da):
       - Router ayarlarına gir
       - Port 8000'i dışarıya aç
       - Modem IP'ni kullan
    """)

if __name__ == "__main__":
    setup_tunnel()
