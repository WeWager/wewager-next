# Generated by Django 3.1.5 on 2021-04-14 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wewager", "0015_auto_20210414_0124"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="league",
            field=models.CharField(default="NBA", max_length=6),
            preserve_default=False,
        ),
    ]
