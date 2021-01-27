# Created Manually on 2021-01-26 08:53

from django.db import migrations
from django.db import models
from parler.models import TranslatableModelMixin

'''
Modifying TIMEREG_TASK_MODE configuration variable -> adding a new option value "List with comments"
'''

def forwards_func(apps, schema_editor):
    ConfigKey = apps.get_model("general", "ConfigKey")
    ConfigKey.__bases__ = (models.Model, TranslatableModelMixin)
    ConfigKeyTranslation = apps.get_model("general", "ConfigKeyTranslation")

    # Get Config key to add key to
    cfg_key = ConfigKey.objects.get(key='TIMEREG_TASK_MODE')

    # Get Config key translation for LITHUANIAN
    cfg_key_translation = ConfigKeyTranslation.objects.get(
        language_code = 'lt',
        master_id = cfg_key.pk,
    )
    # Modify metadata for LITHUANIAN
    cfg_key_translation.metadata = '[(1000,"Sąrašas"), (2000,"Tekstas"), (3000,"Sąrašas su komentaru")], #DEFAULT:1000'
    cfg_key_translation.save()

    # Get Config key translation for NORWEGIAN
    cfg_key_translation = ConfigKeyTranslation.objects.get(
        language_code = 'nb',
        master_id = cfg_key.pk,
    )
    # Modify metadata for NORWEGIAN
    cfg_key_translation.metadata = '[(1000,"Liste"), (2000,"Tekst"), (3000,"Liste med kommentar")], #DEFAULT:1000'
    cfg_key_translation.save()


def reverse_func(apps, schema_editor):
    ConfigKey = apps.get_model("general", "ConfigKey")
    ConfigKey.__bases__ = (models.Model, TranslatableModelMixin)
    ConfigKeyTranslation = apps.get_model("general", "ConfigKeyTranslation")

    # Get Config key to add key to
    cfg_key = ConfigKey.objects.get(key='TIMEREG_TASK_MODE')

    # Get Config key translation for LITHUANIAN
    cfg_key_translation = ConfigKeyTranslation.objects.get(
        language_code = 'lt',
        master_id = cfg_key.pk,
    )
    # Reverse metadata for LITHUANIAN to previous value
    cfg_key_translation.metadata = '[(1000,"Sąrašas"), (2000,"Tekstas")], #DEFAULT:1000'
    cfg_key_translation.save()


    # Get Config key translation for NORWEGIAN
    cfg_key_translation = ConfigKeyTranslation.objects.get(
        language_code = 'nb',
        master_id = cfg_key.pk,
    )
    # Reverse metadata for NORWEGIAN to previous value
    cfg_key_translation.metadata = '[(1000,"Liste"), (2000,"Tekst")], #DEFAULT:1000'
    cfg_key_translation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0017_auto_20200623_1412'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
