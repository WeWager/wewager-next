# Generated by Django 3.1.5 on 2021-04-27 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wewager", "0021_auto_20210423_2139"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="date_eastern",
            field=models.DateTimeField(null=True),
        ),
    ]