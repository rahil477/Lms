#!/usr/bin/env python
"""
Dış ağdan erişim için seçenekler:

1. **ngrok (Ücretsiz, hızlı)**
   - https://ngrok.com/ sitesinden kaydolun
   - Token alın
   - Komutu çalıştırın: ngrok http 8000

2. **Cloudflare Tunnel (Ücretsiz, kalıcı)**
   - https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
   - cloudflared yükleyin: https://github.com/cloudflare/cloudflared
   - Komutu çalıştırın: cloudflared tunnel --url http://localhost:8000

3. **Port Forwarding (Router'da)**
   - Router ayarlarına girin
   - Port 8000'i dışarıya açın
   - Modem'in genel IP'sini kullanın

4. **SSH Tunnel (Eğer SSH sunucusu varsa)**
   - ssh -R 8000:localhost:8000 user@remote-server

Şimdilik Django sunucusunu başlatıyorum:
"""

import os
import subprocess

print(__doc__)

# Django sunucusunu başlat
os.chdir('d:/R/Code/SkyLearn/SkyLearn')
subprocess.run([
    './venv/Scripts/python.exe',
    'manage.py',
    'runserver',
    '0.0.0.0:8000'
])
