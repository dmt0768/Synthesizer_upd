# Generated by Django 2.2.15 on 2020-10-17 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_lines_default_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='lines',
            name='turn_on',
            field=models.BooleanField(default=False),
        ),
    ]
