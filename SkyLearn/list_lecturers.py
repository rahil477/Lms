from accounts.models import User
from django.utils.crypto import get_random_string

# Tüm müellim (öğretmen) listesini göster
print("=" * 70)
print("SKYLEARN - Kayıtlı Müellimler (Öğretmenler)")
print("=" * 70)

lecturers = User.objects.filter(is_lecturer=True).values_list('username', 'email', 'first_name', 'last_name')

if lecturers:
    for username, email, first_name, last_name in lecturers:
        full_name = f"{first_name} {last_name}".strip()
        print(f"Username: {username:15} | Email: {email:25} | {full_name}")
else:
    print("Henüz kayıtlı müellim yok.")

print("=" * 70)
print(f"Toplam: {lecturers.count()} müellim")
