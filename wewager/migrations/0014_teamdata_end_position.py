# Generated by Django 3.1.5 on 2021-02-26 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wewager", "0013_auto_20210225_2255"),
    ]

    operations = [
        migrations.AddField(
            model_name="teamdata",
            name="end_position",
            field=models.IntegerField(null=True),
        ),
    ]