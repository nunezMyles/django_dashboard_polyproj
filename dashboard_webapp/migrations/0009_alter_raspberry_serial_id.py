# Generated by Django 4.1.3 on 2022-12-22 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_webapp', '0008_raspberry_serial_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raspberry',
            name='serial_id',
            field=models.CharField(max_length=200),
        ),
    ]
