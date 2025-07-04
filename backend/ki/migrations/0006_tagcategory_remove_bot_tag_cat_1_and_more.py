# Generated by Django 4.2.11 on 2024-10-11 07:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ki', '0005_uselog_logschool'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagCategory',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=50)),
                ('category_order', models.IntegerField(unique=True)),
            ],
            options={
                'db_table': 'tag_category',
            },
        ),
        migrations.RemoveField(
            model_name='bot',
            name='tag_cat_1',
        ),
        migrations.RemoveField(
            model_name='bot',
            name='tag_cat_2',
        ),
        migrations.RemoveField(
            model_name='bot',
            name='tag_cat_3',
        ),
        migrations.CreateModel(
            name='TagLabel',
            fields=[
                ('tag_label_id', models.AutoField(primary_key=True, serialize=False)),
                ('tag_label_name', models.CharField(max_length=50)),
                ('tag_label_order', models.IntegerField()),
                ('category_id', models.ForeignKey(db_column='category_id', on_delete=django.db.models.deletion.CASCADE, related_name='tag_labels', to='ki.tagcategory')),
            ],
            options={
                'db_table': 'tag_label',
                'unique_together': {('tag_label_order', 'category_id')},
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('tag_id', models.AutoField(primary_key=True, serialize=False)),
                ('tag_value', models.IntegerField()),
                ('bot_id', models.ForeignKey(db_column='bot_id', on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='ki.bot')),
                ('category_id', models.ForeignKey(db_column='category_id', on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='ki.tagcategory')),
            ],
            options={
                'db_table': 'tag',
                'unique_together': {('category_id', 'bot_id')},
            },
        ),
    ]
