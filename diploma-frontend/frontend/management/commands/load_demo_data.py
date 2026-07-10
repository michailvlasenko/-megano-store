from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from frontend.models import (
    Category, Product, ProductImage, Tag, ProductTag,
    ProductSpecification, Review, Sale, Banner, Profile, DeliverySettings
)
from decimal import Decimal
from datetime import timedelta


class Command(BaseCommand):
    help = 'Load demo data for the store'

    def handle(self, *args, **options):
        self.create_users()
        self.create_categories()
        self.create_tags()
        self.create_products()
        self.create_delivery_settings()
        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully!'))

    def create_delivery_settings(self):
        if not DeliverySettings.objects.exists():
            DeliverySettings.objects.create(
                free_delivery_threshold=Decimal('2000'),
                delivery_cost=Decimal('200'),
                express_delivery_cost=Decimal('500'),
            )
            self.stdout.write('  Created delivery settings')

    def create_users(self):
        if not User.objects.filter(username='ivan').exists():
            user = User.objects.create_user('ivan', 'ivan@mail.ru', '123456')
            Profile.objects.create(user=user, full_name='Иван Петров', phone='89001001010')
            self.stdout.write('  Created user: ivan')

        if not User.objects.filter(username='maria').exists():
            user = User.objects.create_user('maria', 'maria@mail.ru', '123456')
            Profile.objects.create(user=user, full_name='Мария Иванова', phone='89002002020')
            self.stdout.write('  Created user: maria')

    def create_categories(self):
        if Category.objects.exists():
            return

        cat_data = [
            ('Электроника', None, [
                ('Смартфоны',),
                ('Ноутбуки',),
                ('Наушники',),
            ]),
            ('Одежда', None, [
                ('Мужская',),
                ('Женская',),
            ]),
            ('Дом и сад', None, [
                ('Мебель',),
                ('Посуда',),
            ]),
        ]

        for cat_title, parent, subs in cat_data:
            cat = Category.objects.create(title=cat_title)
            for sub_title, in subs:
                Category.objects.create(title=sub_title, parent=cat)
            self.stdout.write(f'  Created category: {cat_title}')

    def create_tags(self):
        if Tag.objects.exists():
            return

        tags = ['Gaming', 'Хит', 'Новинка', 'Акция', 'Топ-10']
        for name in tags:
            Tag.objects.create(name=name)
        self.stdout.write(f'  Created {len(tags)} tags')

    def create_products(self):
        if Product.objects.exists():
            return

        categories = list(Category.objects.filter(parent__isnull=False))
        tags = list(Tag.objects.all())

        products_data = [
            {'title': 'iPhone 15 Pro', 'category': 'Смартфоны', 'price': 99990, 'desc': 'Флагманский смартфон Apple с титановым корпусом'},
            {'title': 'Samsung Galaxy S24', 'category': 'Смартфоны', 'price': 89990, 'desc': 'Флагман Samsung с AI-функциями'},
            {'title': 'Xiaomi 14 Pro', 'category': 'Смартфоны', 'price': 69990, 'desc': 'Мощный смартфон с камерой Leica'},
            {'title': 'MacBook Air M3', 'category': 'Ноутбуки', 'price': 129990, 'desc': 'Тонкий и лёгкий ноутбук Apple'},
            {'title': 'Dell XPS 15', 'category': 'Ноутбуки', 'price': 149990, 'desc': 'Премиальный ноутбук с OLED-экраном'},
            {'title': 'ASUS ROG Strix', 'category': 'Ноутбуки', 'price': 179990, 'desc': 'Игровой ноутбук с RTX 4070'},
            {'title': 'AirPods Pro 2', 'category': 'Наушники', 'price': 24990, 'desc': 'Беспроводные наушники с шумоподавлением'},
            {'title': 'Sony WH-1000XM5', 'category': 'Наушники', 'price': 34990, 'desc': 'Лучшие наушники с шумоподавлением'},
            {'title': 'JBL Tune 720BT', 'category': 'Наушники', 'price': 4990, 'desc': 'Доступные беспроводные наушники'},
            {'title': 'Кожаная куртка', 'category': 'Мужская', 'price': 15990, 'desc': 'Натуральная кожа, чёрный цвет'},
            {'title': 'Джинсы классические', 'category': 'Мужская', 'price': 4990, 'desc': 'Классические джинсы синего цвета'},
            {'title': 'Платье вечернее', 'category': 'Женская', 'price': 12990, 'desc': 'Элегантное вечернее платье'},
            {'title': 'Пальто зимнее', 'category': 'Женская', 'price': 24990, 'desc': 'Тёплое зимнее пальто'},
            {'title': 'Диван угловой', 'category': 'Мебель', 'price': 89990, 'desc': 'Удобный угловой диван'},
            {'title': 'Стол письменный', 'category': 'Мебель', 'price': 15990, 'desc': 'Письменный стол из дерева'},
            {'title': 'Набор посуды', 'category': 'Посуда', 'price': 7990, 'desc': 'Набор из 24 предметов'},
        ]

        now = timezone.now()

        for i, p in enumerate(products_data):
            cat = next((c for c in categories if c.title == p['category']), None)
            if not cat:
                continue

            product = Product.objects.create(
                category=cat,
                title=p['title'],
                description=p['desc'],
                full_description=p['desc'] + '. Полное описание товара с детальными характеристиками.',
                price=Decimal(str(p['price'])),
                count=50 - i,
                date=now - timedelta(days=len(products_data) - i),
                free_delivery=(i % 3 == 0),
                rating=Decimal(str(round(4.0 + (i % 5) * 0.2, 2))),
                limited_edition=(i < 3),
                sort_index=len(products_data) - i,
            )

            if i < len(tags):
                ProductTag.objects.create(product=product, tag=tags[i])

            if i < 5:
                ProductSpecification.objects.create(product=product, name='Вес', value=f'{500 + i * 100}г')
                ProductSpecification.objects.create(product=product, name='Цвет', value=['Чёрный', 'Белый', 'Синий'][i % 3])
                ProductSpecification.objects.create(product=product, name='Страна', value='Китай')

            for r in range(i % 4):
                Review.objects.create(
                    product=product,
                    author=f'User_{r + 1}',
                    email=f'user{r}@mail.ru',
                    text='Отличный товар! Всем рекомендую.' if r % 2 == 0 else 'Неплохо, но есть недочёты.',
                    rate=4 + r % 2,
                )

            if i % 3 == 0:
                Sale.objects.create(
                    product=product,
                    sale_price=Decimal(str(round(p['price'] * 0.7, 2))),
                    date_from=now.date() - timedelta(days=5),
                    date_to=now.date() + timedelta(days=10),
                )

            if i < 3:
                Banner.objects.create(product=product)

            self.stdout.write(f'  Created product: {product.title}')

        self.stdout.write(f'  Total products: {Product.objects.count()}')
