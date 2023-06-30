# Generated by Django 2.2.28 on 2023-04-20 08:46

from django.db import migrations
from django.db import models


def forwards_func(apps, schema_editor):

    User = apps.get_model("djauth", "User")
    ContentType = apps.get_model("contenttypes", "ContentType")
    CalendarType = apps.get_model("general", "CalendarType")

    ct = ContentType.objects.get_for_model(User)

    CalendarType.objects.create(
        # Creating Staff Absence due to self-notified illness calendar
        id = 4,
        name = 'STAFF SELF-NOTIFIED ILLNESS',
        owner_type = ct
    )

def reverse_func(apps, schema_editor):
    CalendarType = apps.get_model("general", "CalendarType")
    CalendarType.objects.filter(id=4).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('general', '0021_auto_20230206_0845'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]