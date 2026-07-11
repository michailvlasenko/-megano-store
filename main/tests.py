from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Category, Product, Profile, Cart, Order


class StoreAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = '123456'

        cls.user = User.objects.create_user(
            username='ivan@mail.ru', password=cls.password, email='ivan@mail.ru'
        )
        Profile.objects.create(user=cls.user, full_name='Иван Петров', phone='+79001001010')

        cls.category = Category.objects.create(title='Электроника')
        cls.subcategory = Category.objects.create(title='Смартфоны', parent=cls.category)

        cls.product = Product.objects.create(
            category=cls.subcategory,
            title='iPhone 15 Pro',
            description='Флагманский смартфон',
            price=99990,
            count=10,
        )

    def test_1_sign_up_success(self):
        data = {'name': 'Тест', 'username': 'test@mail.ru', 'password': '123456'}
        response = self.client.post('/api/sign-up', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username='test@mail.ru').exists())

    def test_2_sign_up_duplicate_email(self):
        data = {'name': 'Test', 'username': 'ivan@mail.ru', 'password': '123456'}
        response = self.client.post('/api/sign-up', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_3_sign_up_invalid_email(self):
        data = {'name': 'Test', 'username': 'not-email', 'password': '123456'}
        response = self.client.post('/api/sign-up', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_4_sign_up_short_password(self):
        data = {'name': 'Test', 'username': 'test@mail.ru', 'password': '12'}
        response = self.client.post('/api/sign-up', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_5_sign_in_and_sign_out(self):
        response = self.client.post('/api/sign-in', {
            'username': 'ivan@mail.ru', 'password': self.password
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)

        response = self.client.post('/api/sign-out', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_6_catalog_pagination(self):
        for i in range(25):
            Product.objects.create(
                category=self.subcategory,
                title=f'Product {i}',
                price=100 + i,
                count=5,
            )

        response = self.client.get('/api/catalog?limit=10&currentPage=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 10)
        self.assertEqual(response.data['currentPage'], 1)
        self.assertGreater(response.data['lastPage'], 1)

    def test_7_catalog_filter_by_name(self):
        response = self.client.get('/api/catalog?filter=iPhone')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['title'], 'iPhone 15 Pro')

    def test_8_product_detail(self):
        response = self.client.get(f'/api/product/{self.product.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'iPhone 15 Pro')
        self.assertEqual(response.data['price'], '99990.00')
        self.assertIn('images', response.data)
        self.assertIn('reviews', response.data)

    def test_9_basket_crud(self):
        self.client.force_login(self.user)

        response = self.client.get('/api/basket')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        response = self.client.post('/api/basket', {
            'id': self.product.id, 'count': 2
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get('/api/basket')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.delete('/api/basket', {
            'id': self.product.id, 'count': 2
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_10_profile_auth_required(self):
        response = self.client.get('/api/profile')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_login(self.user)
        response = self.client.get('/api/profile')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['fullName'], 'Иван Петров')
        self.assertEqual(response.data['email'], 'ivan@mail.ru')
        self.assertEqual(response.data['phone'], '+79001001010')

        response = self.client.post('/api/profile', {
            'fullName': 'Новое Имя', 'email': 'ivan@mail.ru', 'phone': '+79001001010'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['fullName'], 'Новое Имя')
