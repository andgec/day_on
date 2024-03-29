# Generated by Django 2.2.28 on 2022-09-24 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('general', '0018_add_cfg_option_20210126_0853'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarHeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=250, verbose_name='name')),
                ('owner_id', models.PositiveIntegerField()),
                ('company', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='general.Company')),
                ('owner_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'calendar',
                'verbose_name_plural': 'calendars',
            },
        ),
        migrations.CreateModel(
            name='CalendarType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=250, verbose_name='name')),
                ('owner_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType', verbose_name='calendar owner type')),
            ],
            options={
                'verbose_name': 'calendar type',
                'verbose_name_plural': 'calendar types',
            },
        ),
        migrations.CreateModel(
            name='CalendarLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, default='', verbose_name='description')),
                ('dfr', models.DateField(verbose_name='date from')),
                ('tfr', models.TimeField(verbose_name='time from')),
                ('dto', models.DateField(verbose_name='date to')),
                ('tto', models.TimeField(verbose_name='time to')),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cal_lines', to='general.CalendarHeader', verbose_name='calendar')),
            ],
            options={
                'verbose_name': 'calendar record',
                'verbose_name_plural': 'calendar records',
            },
        ),
        migrations.AddField(
            model_name='calendarheader',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='calendars', to='general.CalendarType', verbose_name='type'),
        ),
    ]
