# Generated by Django 4.1.3 on 2022-12-22 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_webapp', '0010_remove_raspberry_serial_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='raspberry',
            name='serial_id',
            field=models.CharField(default='RB1', max_length=200),
            preserve_default=False,
        ),
    ]
