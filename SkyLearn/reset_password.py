#!/usr/bin/env python
"""
Django Shell'de Parola Sıfırlama - Hızlı Komutlar

Kullanım:
python manage.py shell
>>> exec(open('reset_password.py').read())
"""

from accounts.models import User
from django.utils.crypto import get_random_string

def reset_password_by_username(username):
    """
    Kullanıcı adına göre parola sıfırla
    """
    try:
        user = User.objects.get(username=username)
        new_password = get_random_string(12)
        user.set_password(new_password)
        user.save()
        
        print("✅ Parola Sıfırlandı!")
        print(f"   Kullanıcı Adı: {user.username}")
        print(f"   Yeni Parola:   {new_password}")
        print(f"   Email:         {user.email}")
        return user, new_password
    except User.DoesNotExist:
        print(f"❌ Hata: '{username}' kullanıcısı bulunamadı!")
        return None, None

def reset_password_by_email(email):
    """
    Email'e göre parola sıfırla
    """
    try:
        user = User.objects.get(email=email)
        new_password = get_random_string(12)
        user.set_password(new_password)
        user.save()
        
        print("✅ Parola Sıfırlandı!")
        print(f"   Kullanıcı Adı: {user.username}")
        print(f"   Yeni Parola:   {new_password}")
        print(f"   Email:         {user.email}")
        return user, new_password
    except User.DoesNotExist:
        print(f"❌ Hata: '{email}' email'ine sahip kullanıcı bulunamadı!")
        return None, None

def list_all_users():
    """
    Tüm kullanıcıları listele
    """
    users = User.objects.filter(is_student=True).values_list('username', 'email', 'first_name', 'last_name')
    
    print("📋 Tüm Öğrenciler:")
    print("=" * 70)
    
    for username, email, first_name, last_name in users:
        full_name = f"{first_name} {last_name}".strip()
        print(f"  Username: {username:15} | Email: {email:25} | {full_name}")
    
    print("=" * 70)
    print(f"Toplam: {users.count()} öğrenci")

# Örnek kullanımlar:
if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════╗
║          SKYLEARN - Parola Sıfırlama Script                        ║
╚════════════════════════════════════════════════════════════════════╝

KULLANIM ÖRNEKLERİ:

1. Django Shell'den çalıştır:
   $ python manage.py shell
   >>> exec(open('reset_password.py').read())
   >>> reset_password_by_username('ugr001')
   
   Çıktı:
   ✅ Parola Sıfırlandı!
      Kullanıcı Adı: ugr001
      Yeni Parola:   aB3cDeFg9hIj
      Email:         ugr001@example.com

2. Email'e göre sıfırla:
   >>> reset_password_by_email('ahmet@example.com')

3. Tüm öğrencileri listele:
   >>> list_all_users()

    """)
