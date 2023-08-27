from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView

from catalog.forms import ProductForm, VersionForm
from catalog.models import Category, Product, Version


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
    form_class = ProductForm
    success_url = reverse_lazy('catalog:categories')
    extra_context = {
        'title': 'Добавить товар',
    }


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('catalog:home')
    extra_context = {
        'title': 'Изменить товар',
    }

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        VersionFormset = inlineformset_factory(Product, Version, form=VersionForm, extra=1)
        if self.request.method == 'POST':
            formset = VersionFormset(self.request.POST, instance=self.object)
        else:
            formset = VersionFormset(instance=self.object)
        context_data['formset'] = formset
        return context_data

    def form_valid(self, form):
        context_data = self.get_context_data()
        formset = context_data['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()

        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('catalog:categories')
