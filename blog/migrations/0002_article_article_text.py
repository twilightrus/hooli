# Generated by Django 2.0.2 on 2018-02-12 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='article_text',
            field=models.TextField(default=''),
        ),
    ]