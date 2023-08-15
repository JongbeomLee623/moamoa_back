# Generated by Django 4.2.4 on 2023-08-15 14:45

from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_scrap_date_scraped'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='image',
        ),
        migrations.AddField(
            model_name='store',
            name='operation_time',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='road_address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='store_num',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='store_other_data',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='Store_Image',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to=main.models.image_upload_path)),
                ('store', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='main.store')),
            ],
        ),
    ]