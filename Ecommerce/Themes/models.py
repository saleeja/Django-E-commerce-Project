from django.db import models

class ThemesSetting(models.Model):
    banner1 = models.ImageField(upload_to='media/site/',blank=True)
    caption1 = models.TextField(blank=True)
    banner2 = models.ImageField(upload_to='media/site/',blank=True)
    caption2 = models.TextField(blank=True)
    banner3 = models.ImageField(upload_to='media/site/',blank=True)
    caption3 = models.TextField(blank=True)
    special_offer_banner = models.ImageField(upload_to='media/site/special_offers/', blank=True, null=True)
    special_offer_caption = models.TextField(blank=True)

   
