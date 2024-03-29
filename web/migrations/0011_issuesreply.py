# Generated by Django 2.2.22 on 2023-04-16 11:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0010_remove_issuestype_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssuesReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply_type', models.IntegerField(choices=[(1, '修改记录'), (2, '回复')], verbose_name='类型')),
                ('content', models.TextField(verbose_name='描述')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='create_reply', to='web.UserInfo', verbose_name='创建者')),
                ('issues', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Issues', verbose_name='问题')),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.IssuesReply', verbose_name='回复')),
            ],
        ),
    ]
