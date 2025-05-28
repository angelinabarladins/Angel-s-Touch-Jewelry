from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    """Категории ювелирных изделий"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class Material(models.Model):
    """Материалы для ювелирных изделий"""
    name = models.CharField(max_length=50, verbose_name="Название материала")
    description = models.TextField(blank=True, verbose_name="Описание")
    price_per_gram = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за грамм"
    )

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.price_per_gram} руб/г)"


class Product(models.Model):
    """Ювелирные изделия"""
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Категория"
    )
    materials = models.ManyToManyField(
        Material,
        through='ProductMaterial',
        verbose_name="Материалы"
    )
    description = models.TextField(verbose_name="Описание")
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        verbose_name="Вес (г)"
    )
    size = models.CharField(max_length=50, blank=True, verbose_name="Размер")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    main_image = models.ImageField(upload_to='products/', verbose_name="Главное изображение")

    class Meta:
        verbose_name = "Изделие"
        verbose_name_plural = "Изделия"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"

    @property
    def price(self):
        """Рассчитывает цену изделия на основе материалов"""
        return sum(
            pm.material.price_per_gram * pm.percentage * self.weight / 100
            for pm in self.product_materials.all()
        )


class ProductMaterial(models.Model):
    """Промежуточная модель для связи изделий и материалов с указанием процентного содержания"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_materials',
        verbose_name="Изделие"
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        verbose_name="Материал"
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Процентное содержание"
    )

    class Meta:
        verbose_name = "Состав изделия"
        verbose_name_plural = "Состав изделий"
        unique_together = [['product', 'material']]

    def __str__(self):
        return f"{self.product}: {self.material} ({self.percentage}%)"


class ProductImage(models.Model):
    """Дополнительные изображения для изделий"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Изделие"
    )
    image = models.ImageField(upload_to='product_images/', verbose_name="Изображение")
    alt_text = models.CharField(max_length=100, blank=True, verbose_name="Альтернативный текст")
    is_main = models.BooleanField(default=False, verbose_name="Главное изображение")

    class Meta:
        verbose_name = "Изображение изделия"
        verbose_name_plural = "Изображения изделий"

    def __str__(self):
        return f"Изображение для {self.product.name}"


class Customer(models.Model):
    """Покупатели"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"


class Order(models.Model):
    """Заказы"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name="Покупатель"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Общая сумма"
    )
    notes = models.TextField(blank=True, verbose_name="Примечания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.strftime('%d.%m.%Y')}"

    @property
    def items_count(self):
        return self.items.count()


class OrderItem(models.Model):
    """Элементы заказа"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Изделие"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за единицу"
    )

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (заказ #{self.order.id})"

    @property
    def total_price(self):
        return self.price * self.quantity


class Review(models.Model):
    """Отзывы о изделиях"""
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Удовлетворительно'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Изделие"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name="Покупатель"
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name="Рейтинг"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
        unique_together = [['product', 'customer']]

    def __str__(self):
        return f"Отзыв от {self.customer} на {self.product} ({self.rating}/5)"

class abExam(models.Model):  
    name = models.CharField(max_length=200, verbose_name="Название экзамена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    exam_date = models.DateField(verbose_name="Дата проведения экзамена")
    exam_image = models.ImageField(upload_to="exam_images/", verbose_name="Задание (изображение)")
    users = models.ManyToManyField(User, related_name="exams", verbose_name="Пользователи")
    is_public = models.BooleanField(default=False, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "Экзамен"
        verbose_name_plural = "Экзамены"

    def __str__(self):
        return self.name
