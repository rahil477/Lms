from accounts.models import User
from django.utils.crypto import get_random_string

# Tüm öğrencileri listele
print("=" * 70)
print("SKYLEARN - Kayıtlı Öğrenciler")
print("=" * 70)

users = User.objects.filter(is_student=True).values_list('username', 'email', 'first_name', 'last_name')

if users:
    for username, email, first_name, last_name in users:
        full_name = f"{first_name} {last_name}".strip()
        print(f"Username: {username:15} | Email: {email:25} | {full_name}")
else:
    print("Henüz kayıtlı öğrenci yok.")

print("=" * 70)
