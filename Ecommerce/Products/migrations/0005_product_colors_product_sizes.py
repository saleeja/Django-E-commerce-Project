# Generated by Django 5.0.3 on 2024-04-11 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0004_color_size_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='colors',
            field=models.ManyToManyField(blank=True, to='Products.color'),
        ),
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=models.ManyToManyField(blank=True, to='Products.size'),
        ),
    ]