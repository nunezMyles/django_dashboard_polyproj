# Generated by Django 4.1.3 on 2022-12-01 15:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_webapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='household',
            old_name='house_block',
            new_name='block',
        ),
    ]