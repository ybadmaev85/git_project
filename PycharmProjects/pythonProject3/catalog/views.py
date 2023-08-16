from django.shortcuts import render

from catalog.models import Category, Product


def con(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        print(f"{name} ({phone}):{message}")
    return render(request, 'catalog/contacts.html')

def home(request):
    context = {
        'object_list': Category.objects.all()[:3],
        'title': 'Главная',
    }
    return render(request, 'catalog/index.html', context)

def categories(request):
    context = {
        'object_list': Category.objects.all(),
        'title': 'Все категории',
    }
    return render(request, 'catalog/categories.html', context)


def products(request, pk):
    category_item = Category.objects.get(pk=pk)
    context = {
        'object_list': Product.objects.filter(category_id=pk),
        'title': f'Товар категории {category_item.name}',
    }
    return render(request, 'catalog/products.html', context)