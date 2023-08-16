from django.urls import path

from catalog.apps import CatalogConfig
from catalog.views import con, home, categories, products

app_name = CatalogConfig.name

urlpatterns = [
    path('', home, name='home'),
    path('categories/', categories, name='categories'),
    path('contacts/', con),
    path('<int:pk>/products/', products, name='products')
]