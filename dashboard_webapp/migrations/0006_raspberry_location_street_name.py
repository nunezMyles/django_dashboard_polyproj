# Generated by Django 4.1.3 on 2022-12-15 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_webapp', '0005_alter_smokereading_smoke_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='raspberry_location',
            name='street_name',
            field=models.CharField(default='Fernvale Link', max_length=200),
            preserve_default=False,
        ),
    ]
