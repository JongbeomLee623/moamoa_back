# Generated by Django 4.1.7 on 2023-08-15 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_review_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='date',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='review',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]