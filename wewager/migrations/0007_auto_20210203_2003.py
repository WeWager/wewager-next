# Generated by Django 3.1.5 on 2021-02-03 20:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("wewager", "0006_auto_20210203_1948"),
    ]

    operations = [
        migrations.AddField(
            model_name="wallet",
            name="user",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.DeleteModel(
            name="Account",
        ),
    ]
