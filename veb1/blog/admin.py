from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Material, Product, ProductMaterial, 
    ProductImage, Customer, Order, OrderItem, Review
)


class ProductMaterialInline(admin.TabularInline):
    model = ProductMaterial
    extra = 1
    raw_id_fields = ['material']
    verbose_name = "Состав изделия"
    verbose_name_plural = "Состав изделия"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']
    verbose_name = "Изображение"
    verbose_name_plural = "Дополнительные изображения"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="100" />', obj.image.url)
        return "-"
    image_preview.short_description = "Превью"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count', 'slug']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['product_count']

    @admin.display(description='Количество изделий')
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_gram']
    list_filter = ['price_per_gram']
    search_fields = ['name']
    list_display_links = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'category', 
        'display_price', 
        'weight', 
        'is_available', 
        'created_at'
    ]
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = []
    raw_id_fields = ['category']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [ProductMaterialInline, ProductImageInline]
    list_display_links = ['name', 'category']

    @admin.display(description='Цена', ordering='price')
    def display_price(self, obj):
        return f"{obj.price:.2f} руб"
    display_price.short_description = "Цена"


@admin.register(ProductMaterial)
class ProductMaterialAdmin(admin.ModelAdmin):
    list_display = ['product', 'material', 'percentage']
    list_filter = ['material']
    raw_id_fields = ['product']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'order_count']
    list_filter = ['user__date_joined']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    raw_id_fields = ['user']
    readonly_fields = ['order_count']

    @admin.display(description='Количество заказов')
    def order_count(self, obj):
        return obj.orders.count()


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ['product']
    readonly_fields = ['total_price']
    verbose_name = "Элемент заказа"
    verbose_name_plural = "Элементы заказа"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'customer', 
        'status', 
        'total', 
        'created_at', 
        'items_display'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'customer__user__first_name', 
        'customer__user__last_name',
        'id'
    ]
    raw_id_fields = ['customer']
    readonly_fields = ['created_at', 'updated_at', 'total']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    list_editable = ['status']

    @admin.display(description='Товары')
    def items_display(self, obj):
        items = obj.items.all()[:3]
        items_list = [f"{item.product.name} x{item.quantity}" for item in items]
        if obj.items.count() > 3:
            items_list.append("...")
        return ", ".join(items_list)
    items_display.short_description = "Товары в заказе"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'rating', 'created_at', 'is_published']
    list_filter = ['rating', 'is_published', 'created_at']
    search_fields = ['product__name', 'customer__user__first_name', 'text']
    raw_id_fields = ['product', 'customer']
    readonly_fields = ['created_at']
    list_editable = ['is_published']
    date_hierarchy = 'created_at'

form = ProductAdminForm  # для ProductAdmin
form = OrderAdminForm    # для OrderAdmin
