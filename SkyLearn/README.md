![Group 23](https://github.com/user-attachments/assets/4e84251a-27b0-462b-bd5e-fb0bcadc4694)

### The world’s most high-end designed, lightweight, and feature-rich learning management system.

# LMS (Customized SkyLearn)

Bu layihə orijinal **SkyLearn** (Open source learning management system) əsasında yaradılmış və xüsusi ehtiyaclara uyğunlaşdırılmış Tədris İdarəetmə Sistemidir (LMS). Layihə Django web framework ilə yazılıb. 

Orijinal repositoriya: [SkyLearn](https://github.com/SkyCascade/SkyLearn)  
Mövcud repositoriya: [rahil477/LMS](https://github.com/rahil477/LMS)

---

## 🛠 Nələr Dəyişdirilib və Əlavə Edilib? (Customizations)

Orijinal SkyLearn üzərində aşağıdakı əsas dəyişikliklər və düzəlişlər edilmişdir:

1. **Bug Fixes (Xəta Həlləri):**
   - **TemplateSyntaxError həlli:** `sidebar.html` faylında qlobal olaraq bütün səhifələri çökdürən tərcümə və şablon xətası (`lang.code==LANGUAGE_CODE` boşluq problemi) düzəldildi.
   - **Tərcümə (i18n) Xətalarının Həlli:** Tələbə və müəllim siyahılarında ("Add Student" kimi) tərcümə taglarının işləməməsi və ekranda literal tagların (`{% trans 'Add Student' %}`) görünməsi problemi aradan qaldırıldı.

2. **Dillər və Tərcümə:**
   - Azərbaycan dili (az) dəstəyi tam formalaşdırıldı və default dil olaraq sazlandı.
   - UI komponentləri, menyular və formlar lokallaşdırıldı.

3. **Hesabların İdarəedilməsi və Təhlükəsizlik:**
   - İstifadəçi adı və parolların təhlükəsiz və düzgün formalaşdırılması sistemi təkmilləşdirildi (Ad.Soyad formatında avtomatik istifadəçi adlarının təyin edilməsi).

---

## 🚀 Quraşdırma (Installation)

Layihəni öz kompyuterinizdə və ya serverinizdə işə salmaq üçün aşağıdakı addımları izləyin:

### Tələblər:
- Python 3.8+
- Git

### Addım-addım quraşdırma:

1. **Repozitoriyanı klonlayın:**
   ```bash
   git clone https://github.com/rahil477/LMS.git
   cd LMS
   ```

2. **Virtual mühit (Virtual Environment) yaradın və aktivləşdirin:**
   - Windows üçün:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - Mac/Linux üçün:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Asılılıqları (Dependencies) yükləyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Kataloqa daxil olun və `.env` faylını yaradın:**
   ```bash
   cd SkyLearn
   ```
   *Qeyd: `.env.example` faylının içindəki məlumatları kopyalayıb eyni qovluqda `.env` adlı fayl yaradın və ora yapışdırın.*

5. **Məlumat bazasını qurmaq üçün miqrasiyaları işə salın:**
   ```bash
   python manage.py migrate
   ```

6. **Admin hesabı yaradın:**
   ```bash
   python manage.py createsuperuser
   ```
   *(Ekranda sizdən username, email və password istəniləcək)*

7. **Serveri işə salın:**
   ```bash
   python manage.py runserver
   ```

Artıq sayt lokal serverinizdə işləktir. Brauzerinizdə daxil olun: **http://127.0.0.1:8000**

---

## 📖 Necə İstifadə Edilir? (Usage Guide)

Sistemdə əsasən 3 rol var: **Admin, Müəllim (Lecturer) və Tələbə (Student).**

### 1. Panelə Giriş
- Quraşdırma zamanı yaratdığınız **Superuser (Admin)** parolu ilə http://127.0.0.1:8000/en/accounts/login/ (və ya əsas səhifədəki Login düyməsi ilə) sistemə daxil olun.

### 2. Tələbə və Müəllim Əlavə etmək
- **İstifadəçi Yaratmaq:** Admin Panelindən (sol menyudakı "Students" və ya "Lecturers" bölməsi) yeni tələbə və müəllimlər yarada bilərsiniz. 
- Yaratdığınız hər bir profil üçün **Username** və **Password** təyin edin.
- *Əgər parolları sonradan dəyişmək lazımdırsa:* Bunu Django-nun əsas admin panelindən (`http://127.0.0.1:8000/admin/`) "Users" bölməsinə daxil olaraq "change password" linki ilə edə bilərsiniz.

### 3. Kurslar və Fənlər
- **"Programs & Courses"** bölməsindən yeni tədris proqramları və fənlər əlavə edin.
- Hər kursa spesifik müəllim təyin edə ("Course Allocation") və qiymətləndirmə meyarları yarada bilərsiniz.

### 4. Davamiyyət və Qiymətlər
- Müəllimlər sistemə öz hesabları (username/password) ilə daxil olaraq onlara təyin edilmiş fənlər üzrə tələbələrin **davamiyyətini yoxlaya** və **imtahan/tapşırıq qiymətlərini** daxil edə bilərlər.

### 5. Avtomatik Hesablamalar
- Sistem tələbələrin ballarını (Mid exam, Final exam, assignment) avtomatik toplayaraq nəticəni (Pass/Fail) özü hesablayır. Tələbələr isə öz hesablarına girərək profillərindən qiymət cədvəllərini və davamiyyətlərini görə bilərlər.

---

> Bu versiya açıq mənbəli (Open Source) SkyLearn layihəsinin xətalardan təmizlənmiş və lokallaşdırılmış forkudur. Sual və ya problemlər yaranarsa GitHub "Issues" bölməsindən istifadə edə bilərsiniz.
