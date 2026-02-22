from django.utils.text import slugify
from accounts.models import User

def generate_username_from_fullname(first_name, last_name):
    if not first_name or not last_name:
        return None
    
    base_username = "{}.{}".format(first_name, last_name).lower()
    username = slugify(base_username)
    
    counter = 1
    original_username = username
    while User.objects.filter(username=username).exists():
        username = "{}{}".format(original_username, counter)
        counter += 1
    
    return username

def update_all_usernames():
    print("=" * 70)
    print("SKYLEARN - Username Guncelleme")
    print("=" * 70)
    
    users = User.objects.filter(first_name__isnull=False, last_name__isnull=False).exclude(
        first_name='', last_name=''
    )
    
    if not users:
        print("Guncelleme yapilacak kullanici yok.")
        return
    
    updated_count = 0
    for user in users:
        old_username = user.username
        new_username = generate_username_from_fullname(user.first_name, user.last_name)
        
        if new_username and old_username != new_username:
            user.username = new_username
            user.save()
            updated_count += 1
            print("OK: {} : {} -> {}".format(user.get_full_name[:30], old_username, new_username))
        else:
            print("SKIP: {} : {}".format(user.get_full_name[:30], old_username))
    
    print("=" * 70)
    print("Toplam guncellenen: {}".format(updated_count))
    print("=" * 70)

update_all_usernames()
