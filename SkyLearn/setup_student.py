#!/usr/bin/env python
"""
Django ortamında öğrenci oluşturma ve parola ayarlama script'i
Kullanım: python manage.py shell < setup_student.py
"""

import os
import django
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, Student

def create_student_with_password(username, first_name, last_name, email, program, admission_year):
    """
    Öğrenci oluştur ve parola ayarla
    
    Args:
        username: Kullanıcı adı (örn: ugr001)
        first_name: Adı
        last_name: Soyadı
        email: E-posta
        program: Program (Program nesnesi)
        admission_year: Başlama yılı
    
    Returns:
        user, password tuple
    """
    
    # Rastgele parola oluştur
    password = get_random_string(12, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%')
    
    # User oluştur
    user = User.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        is_student=True,
        is_active=True
    )
    
    # Student kaydı oluştur
    student = Student.objects.create(
        user=user,
        id_number=username,
        level=program.level if hasattr(program, 'level') else '100',
        admission_year=admission_year,
        program=program
    )
    
    return user, password

# Örnek kullanım:
if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         SKYLEARN - Student Creation Script                 ║
    ║                                                             ║
    ║  Django Shell'den çalıştırmak için:                        ║
    ║  python manage.py shell                                    ║
    ║  >>> exec(open('setup_student.py').read())                 ║
    ║                                                             ║
    ║  Veya doğrudan çalıştırmak için:                           ║
    ║  python setup_student.py                                   ║
    ╚════════════════════════════════════════════════════════════╝
    
    Kullanım örneği:
    
    from setup_student import create_student_with_password
    from course.models import Program
    
    # Program'ı al
    program = Program.objects.first()
    
    # Öğrenci oluştur
    user, password = create_student_with_password(
        username='ugr001',
        first_name='Ahmet',
        last_name='Yılmaz',
        email='ahmet@example.com',
        program=program,
        admission_year=2024
    )
    
    print(f"Kullanıcı Adı: {user.username}")
    print(f"Parola: {password}")
    """)
