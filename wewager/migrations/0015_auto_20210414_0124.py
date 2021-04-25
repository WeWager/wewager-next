# Generated by Django 3.1.5 on 2021-04-14 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wewager', '0014_teamdata_end_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='teamUid',
            field=models.CharField(max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='teamdata',
            name='moneyline',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='teamdata',
            name='spread',
            field=models.DecimalField(decimal_places=1, max_digits=3, null=True),
        ),
    ]
