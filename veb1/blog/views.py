from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Order, abExam
from django.db.models import Count, Avg
from django.db.models import Q  

def home(request):
    popular_products = Product.objects.all() 
    new_arrivals = Product.objects.order_by('-created_at')[:5]
    average_price = Product.objects.aggregate(Avg('price'))['price__avg']
    discounted_products = Product.objects.filter(price__lt=average_price)[:5]
    # Поиск
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
        'search_results': results, 
        'search_query': query, 
    }
    return render(request, 'blog/home.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'blog/product_detail.html', {'product': product})

def ab_exam_view(request):
    exams = abExam.objects.filter(is_public=True)
    context = {
        'fio': 'Барладина Ангелина Александровна, группа 241-671',
        'exams': exams,
    }
    return render(request, 'blog/ab_exam.html', context)
