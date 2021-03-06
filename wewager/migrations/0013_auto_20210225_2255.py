# Generated by Django 3.1.5 on 2021-02-25 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wewager", "0012_auto_20210225_2113"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="gameUid",
            field=models.CharField(default="xxxxxxx", max_length=7),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="team",
            name="teamUid",
            field=models.CharField(default="xxxxxxx", max_length=7),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="teamdata",
            name="winning_position",
            field=models.IntegerField(default=1),
        ),
    ]
