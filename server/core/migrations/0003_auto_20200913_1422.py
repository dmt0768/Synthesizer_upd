# Generated by Django 2.2.15 on 2020-09-13 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200909_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registers',
            name='value',
            field=models.IntegerField(),
        ),
    ]
