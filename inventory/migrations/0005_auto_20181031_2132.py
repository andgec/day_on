# Generated by Django 2.1.1 on 2018-10-31 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_auto_20181025_0901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Price'),
        ),
    ]
