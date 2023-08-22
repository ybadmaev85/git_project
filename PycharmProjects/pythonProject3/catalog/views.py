from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from catalog.models import Category, Product


def con(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        print(f"{name} ({phone}):{message}")
    return render(request, 'catalog/contacts.html')


class IndexView(TemplateView):
    template_name = 'catalog/index.html'
    extra_context = {
        'title': 'Главная'
    }

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['object_list'] = Category.objects.all()[:3]
        return context_data


# def home(request):
#     context = {
#         'object_list': Category.objects.all()[:3],
#         'title': 'Главная',
#     }
#     return render(request, 'catalog/index.html', context)

# def categories(request):
#     context = {
#         'object_list': Category.objects.all(),
#         'title': 'Все категории',
#     }
#     return render(request, 'catalog/category_list.html', context)

class CategoryListView(ListView):
    model = Category
    extra_context = {
        'title': 'Все категории'
    }

# def products(request, pk):
#     category_item = Category.objects.get(pk=pk)
#     context = {
#         'object_list': Product.objects.filter(category_id=pk),
#         'title': f'Товар категории {category_item.name}',
#     }
#     return render(request, 'catalog/product_list.html', context)

class ProductListView(ListView):
    model = Product

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(category_id=self.kwargs.get('pk'))
        return queryset

    def get_context_data(self, *args, **kwargs):

        category_item = Category.objects.get(pk=self.kwargs.get('pk'))
        context_data = super().get_context_data(*args, **kwargs)
        context_data['category_pk'] = category_item.pk
        context_data['title'] = f'Товар категории {category_item.name}'

        return context_data


class ProductCreateView(CreateView):
    model = Product
    fields = ('name', 'description', 'photo', 'category', 'price')
    success_url = reverse_lazy('catalog:categories')

class ProductUpdateView(UpdateView):
    model = Product
    fields = ('name', 'description', 'photo', 'category')
    success_url = reverse_lazy('catalog:home')

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('catalog:categories')