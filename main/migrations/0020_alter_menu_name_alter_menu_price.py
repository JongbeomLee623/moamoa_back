# Generated by Django 4.2.4 on 2023-08-16 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_rename_date_review_created_at_review_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='menu',
            name='price',
            field=models.CharField(max_length=255),
        ),
    ]
