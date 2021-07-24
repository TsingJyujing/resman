# Generated by Django 3.1.4 on 2021-07-24 13:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('event_type', models.CharField(max_length=100)),
                ('media_type', models.CharField(max_length=100)),
                ('data', models.TextField(default='{}')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['created'], name='data_event_created_0bd908_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['user', 'event_type', 'media_type'], name='data_event_user_id_0f3d59_idx'),
        ),
    ]
