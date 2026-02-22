from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.text import slugify
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Student, Parent


class UserAdmin(BaseUserAdmin):
    list_display = [
        "get_full_name",
        "username",
        "email",
        "is_active",
        "is_student",
        "is_lecturer",
        "is_parent",
        "is_staff",
    ]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_lecturer",
        "is_parent",
        "is_staff",
    ]
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("is_student", "is_lecturer", "is_parent", "is_dep_head", "gender", "phone", "address", "picture")}),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Ad ve soyaddan otomatik username oluştur
        Örnek: "Rahil Menefzade" -> "rahil.menefzade"
        """
        if not change:  # Yeni user oluşturuluyorsa
            if obj.first_name and obj.last_name:
                # Ad.Soyad formatında username oluştur
                base_username = f"{obj.first_name.lower()}.{obj.last_name.lower()}"
                # Türkçe karakterleri düzelt
                base_username = slugify(base_username)
                
                # Eğer böyle bir username zaten varsa, numarası ekle
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                obj.username = username
        
        super().save_model(request, obj, form, change)

    class Meta:
        managed = True
        verbose_name = "User"
        verbose_name_plural = "Users"


admin.site.register(User, UserAdmin)
admin.site.register(Student)
admin.site.register(Parent)
