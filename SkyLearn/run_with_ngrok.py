#!/usr/bin/env python
"""Run Django with ngrok tunnel for external network access"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from pyngrok import ngrok

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def main():
    # Start ngrok tunnel
    print("Starting ngrok tunnel...")
    public_url = ngrok.connect(8000, "http")
    print(f"\n{'='*60}")
    print(f"✅ PUBLIC URL: {public_url}")
    print(f"✅ LOCAL URL: http://127.0.0.1:8000")
    print(f"{'='*60}\n")
    
    # Start Django server
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])

if __name__ == '__main__':
    main()
