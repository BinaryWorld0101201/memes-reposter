# Generated by Django 2.0.3 on 2018-07-26 21:26

import apps.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0004_auto_20180726_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='media_link',
            field=apps.core.fields.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='media_type',
            field=models.CharField(choices=[('link', 'link'), ('text', 'text'), ('photo', 'photo'), ('video', 'video')], default='link', max_length=200),
        ),
        migrations.AddField(
            model_name='post',
            name='nsfw',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='score',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
    ]