# Generated by Django 4.2.11 on 2024-09-24 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ki', '0004_auto_20240918_0711'),
    ]

    operations = [
        migrations.CreateModel(
            name='UseLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('role', models.CharField(max_length=20)),
                ('bot_id', models.CharField(max_length=36)),
                ('message_length', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'use_log',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='LogSchool',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('log_id', models.ForeignKey(db_column='log_id', on_delete=django.db.models.deletion.CASCADE, related_name='schools', to='ki.uselog')),
                ('school_id', models.ForeignKey(db_column='school', on_delete=django.db.models.deletion.DO_NOTHING, related_name='school_logs', to='ki.school')),
            ],
            options={
                'db_table': 'log_school',
                'unique_together': {('log_id', 'school_id')},
            },
        ),
    ]
