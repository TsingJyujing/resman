# Generated by Django 3.2.19 on 2023-05-07 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_auto_20230505_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='size',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='s3image',
            name='size',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='s3video',
            name='size',
            field=models.BigIntegerField(null=True),
        ),
    ]