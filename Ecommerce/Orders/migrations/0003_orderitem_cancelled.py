# Generated by Django 5.0.3 on 2024-04-14 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
    ]