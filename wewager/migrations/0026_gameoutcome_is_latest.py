# Generated by Django 3.1.8 on 2021-05-06 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wewager', '0025_delete_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameoutcome',
            name='is_latest',
            field=models.BooleanField(default=True),
        ),
    ]
