# Generated by Django 4.0.3 on 2022-04-11 21:18
from django.contrib.postgres.operations import TrigramExtension, CITextExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        TrigramExtension(),
        CITextExtension(),
    ]
