# Generated by Django 3.2.4 on 2021-07-04 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='winner',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
