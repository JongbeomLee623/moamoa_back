# Generated by Django 4.1.7 on 2023-08-15 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_alter_chat_wordcloud_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='wordcloud_image',
            field=models.ImageField(default='default_wordcloud.png', upload_to='chat'),
        ),
    ]
