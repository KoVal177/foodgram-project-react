# Generated by Django 3.2 on 2023-01-29 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='cook_time',
            new_name='cooking_time',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='color_code',
            new_name='color',
        ),
    ]
