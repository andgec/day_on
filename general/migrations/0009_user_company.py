from django.db import migrations

def insert_system_company(apps, schema_editor):
    Company = apps.get_model('general', 'Company')
    company = Company(name='My Company', number='0123456789')
    company.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('general', '0008_auto_20181024_1457'),
    ]

    operations = [
        migrations.RunPython(insert_system_company),
    ]
