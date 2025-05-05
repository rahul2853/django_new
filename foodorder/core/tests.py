from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, FoodItem

class FoodOrderTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
        )
        
        # Create test food items
        self.food1 = FoodItem.objects.create(
            name='Test Food 1',
            description='Test Food 1 Description',
            price='9.99',
            category=self.category,
            is_available=True
        )
        
        self.food2 = FoodItem.objects.create(
            name='Test Food 2',
            description='Test Food 2 Description',
            price='14.99',
            category=self.category,
            is_available=True
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Test Category')

    def test_menu_page(self):
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu.html')
        self.assertContains(response, 'Test Food 1')
        self.assertContains(response, 'Test Food 2')

    def test_login(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'testuser', 'password': 'testpass123'},
            follow=True
        )
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('home'))

    def test_cart_functionality(self):
        # Add an item to the cart
        response = self.client.post(
            reverse('cart_add', args=[self.food1.id]),
            {'quantity': 2}
        )
        self.assertRedirects(response, reverse('cart_detail'))
        
        # Check cart contents
        response = self.client.get(reverse('cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Food 1')
        self.assertContains(response, '9.99')
