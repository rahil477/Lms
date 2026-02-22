"""
Django Admin'de Öğrenci Oluşturulduktan Sonra Parola Gösterme Rehberi

SORUN: Admin panelinde yeni öğrenci (user) oluşturduktan sonra parola nereden öğrenilir?

ÇÖZÜM 1: Django Built-in - Admin Panelinde Parola Sıfırlama Linki
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Eğer admin panelinde user oluşturduktan sonra parola ayarlamak isterseniz:

1. User'ı oluşturduktan sonra:
   - Admin panelinde User listesine git
   - Oluşturduğun user'ı seç
   - "Parola değiştir" bağlantısını tıkla
   - Yeni parola belirle

2. Ya da admin panelinde user düzenleme sayfasında:
   - "Password" alanında "change password form" linkini aç
   - Yeni parola gir
   - Kaydet


ÇÖZÜM 2: Django Shell'de Parola Ayarlama
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Terminalde:
$ python manage.py shell

>>> from accounts.models import User
>>> from django.contrib.auth.models import User
>>> from django.utils.crypto import get_random_string
>>> 
>>> # User'ı bul
>>> user = User.objects.get(username='ugr001')
>>> 
>>> # Parola oluştur ve ayarla
>>> password = 'TempPassword123!'
>>> user.set_password(password)
>>> user.save()
>>> 
>>> print(f"Username: {user.username}")
>>> print(f"Password: {password}")


ÇÖZÜM 3: Otomatik Parola Oluşturma (Programatik)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$ python manage.py shell

>>> from setup_student import create_student_with_password
>>> from course.models import Program
>>> 
>>> program = Program.objects.first()
>>> user, password = create_student_with_password(
...     username='ugr002',
...     first_name='Ayşe',
...     last_name='Demir',
...     email='ayse@example.com',
...     program=program,
...     admission_year=2024
... )
>>>
>>> print(f"Kullanıcı Adı: {user.username}")
>>> print(f"Otomatik Parola: {password}")
>>> print(f"Email: {user.email}")


ÇÖZÜM 4: Hızlı Parola Belirleme Komutu
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Terminalde direkt:
$ python manage.py shell -c "from accounts.models import User; u=User.objects.get(username='ugr001'); u.set_password('ParolaGir123'); u.save(); print(f'User: {u.username}, Pass set')"


ÖNERİLEN YÖNTEM: 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Admin panelinde User oluştur → Ardından Django Shell'den otomatik parola oluştur:

python manage.py shell

>>> from setup_student import create_student_with_password
>>> from course.models import Program
>>>
>>> # Var olan user'a sadece parola ata
>>> from accounts.models import User
>>> from django.utils.crypto import get_random_string
>>>
>>> user = User.objects.get(username='ugr001')
>>> password = get_random_string(12)
>>> user.set_password(password)
>>> user.save()
>>>
>>> print(f"User: {user.username}")
>>> print(f"New Password: {password}")
>>> print(f"Email: {user.email}")

Çıktı:
User: ugr001
New Password: aB3cDeFg9hIj
Email: ugr001@example.com

⭐ Bu parolayı öğrenciye bildir!
"""

print(__doc__)
