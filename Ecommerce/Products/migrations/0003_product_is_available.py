# Generated by Django 5.0.3 on 2024-04-10 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0002_subcategory_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]