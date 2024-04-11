from django.urls import path
from .views import upload_theme
urlpatterns = [
    path('upload/', upload_theme, name='upload_theme'),

]
