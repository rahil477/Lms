from course.models import Program

for pg in Program.objects.all():
    if pg.id == 1:
        pg.title = 'Qrafik Dizayn'
        if hasattr(pg, 'title_az'):
            pg.title_az = 'Qrafik Dizayn'
            pg.title_en = 'Graphic Design'
        pg.save()
    elif pg.id == 2:
        pg.title = 'SMM'
        if hasattr(pg, 'title_az'):
            pg.title_az = 'SMM'
            pg.title_en = 'SMM'
        pg.save()

print("Programs updated:")
for pg in Program.objects.all():
    print(f"After ID: {pg.id} title: '{pg.title}'")
