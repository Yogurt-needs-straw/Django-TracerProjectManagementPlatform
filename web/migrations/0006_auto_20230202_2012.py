# Generated by Django 2.2.22 on 2023-02-02 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_wiki_depth'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='bucket',
            field=models.CharField(default='xxx', max_length=128, verbose_name='COS桶'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='region',
            field=models.CharField(default='xxx', max_length=32, verbose_name='COS区域'),
            preserve_default=False,
        ),
    ]
