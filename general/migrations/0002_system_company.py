from django.db import migrations

def insert_system_company(apps, schema_editor):
    Company = apps.get_model('general', 'Company')
    company = Company(name='system', number='xxxxxxxx')
    company.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_system_company),
    ]
