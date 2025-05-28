from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Order
from django.db.models import Count, Avg
from django.db.models import Q  # Import Q for complex lookups

def home(request):
    # 1. Популярные продукты (самые просматриваемые или покупаемые)
    # Пример: Считаем количество заказов для каждого продукта (пока просто все продукты)
    popular_products = Product.objects.all()  #Можно добавить логику подсчета просмотров/покупок, но пока просто список

    # 2. Новые поступления (товары, добавленные недавно)
    new_arrivals = Product.objects.order_by('-created_at')[:5]

    # 3. Товары со скидкой (пример, пока нет поля "скидка", используем товары, цена которых ниже средней)
    average_price = Product.objects.aggregate(Avg('price'))['price__avg']
    discounted_products = Product.objects.filter(price__lt=average_price)[:5] #Товары ниже средней цены

    #4. Поиск
    query = request.GET.get('q')
    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        'popular_products': popular_products,
        'new_arrivals': new_arrivals,
        'discounted_products': discounted_products,
        'search_results': results,  # Передаем результаты поиска
        'search_query': query,  # Передаем поисковый запрос
    }
    return render(request, 'blog/home.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'blog/product_detail.html', {'product': product})
