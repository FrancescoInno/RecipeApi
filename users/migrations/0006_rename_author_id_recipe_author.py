# Generated by Django 4.2.2 on 2023-06-07 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_rename_author_recipe_author_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='author_id',
            new_name='author',
        ),
    ]
