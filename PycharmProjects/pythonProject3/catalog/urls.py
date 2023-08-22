from django.urls import path

from catalog.apps import CatalogConfig
from catalog.views import con, IndexView, CategoryListView, ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView

app_name = CatalogConfig.name

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('contacts/', con),
    path('<int:pk>/products/', ProductListView.as_view(), name='products'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/update/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('products/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
]