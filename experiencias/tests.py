from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Role, User, UserRole
from experiencias.models import Category, Experience, Reservation


class RoleWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_role, _ = Role.objects.update_or_create(
            role_name=Role.ADMINISTRATOR,
            defaults={'administrador': 2, 'guia': 0, 'operador': 0, 'turista': 0, 'cliente': 0},
        )
        cls.guide_role, _ = Role.objects.update_or_create(
            role_name=Role.GUIDE_OPERATOR,
            defaults={'administrador': 0, 'guia': 2, 'operador': 2, 'turista': 0, 'cliente': 0},
        )
        cls.tourist_role, _ = Role.objects.update_or_create(
            role_name=Role.TOURIST_CLIENT,
            defaults={'administrador': 0, 'guia': 0, 'operador': 0, 'turista': 2, 'cliente': 2},
        )
        cls.admin = User.objects.create_superuser(
            username='admin-test',
            email='admin@example.test',
            password='test-password-123!',
        )
        cls.guide = User.objects.create_user(
            username='guide-test',
            password='test-password-123!',
        )
        cls.other_guide = User.objects.create_user(
            username='guide-other',
            password='test-password-123!',
        )
        cls.tourist = User.objects.create_user(
            username='tourist-test',
            password='test-password-123!',
        )
        cls.other_tourist = User.objects.create_user(
            username='tourist-other',
            password='test-password-123!',
        )
        UserRole.objects.create(user_id=cls.guide, role=cls.guide_role)
        UserRole.objects.create(user_id=cls.other_guide, role=cls.guide_role)
        UserRole.objects.create(user_id=cls.tourist, role=cls.tourist_role)
        UserRole.objects.create(user_id=cls.other_tourist, role=cls.tourist_role)

        cls.category = Category.objects.create(
            name='Trekking',
            description='Senderos naturales',
        )
        cls.experience = cls.create_experience(
            title='Experiencia propia',
            creator=cls.guide,
            category=cls.category,
        )
        cls.other_experience = cls.create_experience(
            title='Experiencia ajena',
            creator=cls.other_guide,
            category=cls.category,
        )

    @classmethod
    def create_experience(cls, title, creator, category, capacity=3, is_active=True):
        return Experience.objects.create(
            title=title,
            description='Descripción de prueba',
            price=Decimal('10000.00'),
            capacity=capacity,
            scheduled_at=timezone.now() + timedelta(days=10),
            category=category,
            creator=creator,
            is_active=is_active,
        )

    def test_guide_only_lists_and_updates_own_experiences(self):
        self.client.force_login(self.guide)
        response = self.client.get(reverse('experience_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.experience.title)
        self.assertNotContains(response, self.other_experience.title)

        response = self.client.get(
            reverse('experience_update', args=[self.other_experience.pk])
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            self.client.get(reverse('experience_delete', args=[self.experience.pk])).status_code,
            403,
        )

    def test_tourist_can_reserve_once_and_only_sees_personal_history(self):
        self.client.force_login(self.tourist)
        response = self.client.post(
            reverse('reservation_create', args=[self.experience.pk])
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            reverse('reservation_create', args=[self.experience.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Reservation.objects.filter(user=self.tourist, experience=self.experience).count(),
            1,
        )

        Reservation.objects.create(user=self.other_tourist, experience=self.other_experience)
        response = self.client.get(reverse('reservation_list'))
        self.assertContains(response, self.experience.title)
        self.assertNotContains(response, self.other_experience.title)

    def test_tourist_cannot_overbook_experience(self):
        experience = self.create_experience(
            title='Cupo único',
            creator=self.guide,
            category=self.category,
            capacity=1,
        )
        Reservation.objects.create(user=self.tourist, experience=experience)
        self.client.force_login(self.other_tourist)

        response = self.client.post(reverse('reservation_create', args=[experience.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reservation.objects.filter(experience=experience).count(), 1)

    def test_only_administrator_can_manage_categories(self):
        self.client.force_login(self.guide)
        self.assertEqual(self.client.get(reverse('category_list')).status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('category_create'),
            {'name': 'Kayak', 'description': 'Paseos en kayak', 'is_active': 'on'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Kayak').exists())

    def test_administrator_can_render_management_lists_and_delete_confirmations(self):
        self.client.force_login(self.admin)
        route_names = [
            'experience_list',
            'category_list',
            'reservation_list',
            'user_list',
        ]
        for route_name in route_names:
            with self.subTest(route=route_name):
                self.assertEqual(self.client.get(reverse(route_name)).status_code, 200)

        self.assertEqual(self.client.get(reverse('experience_create')).status_code, 200)
        self.assertEqual(self.client.get(reverse('category_create')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('experience_delete', args=[self.experience.pk])).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('category_delete', args=[self.category.pk])).status_code,
            200,
        )

    def test_public_catalog_only_shows_active_upcoming_experiences(self):
        inactive = self.create_experience(
            title='Experiencia inactiva',
            creator=self.guide,
            category=self.category,
            is_active=False,
        )
        response = self.client.get(reverse('catalog'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.experience.title)
        self.assertNotContains(response, inactive.title)


class DemoDataCommandTests(TestCase):
    def test_seed_command_creates_required_demo_accounts_and_reservations(self):
        output = StringIO()

        call_command('seed_demo_data', stdout=output)

        guides = User.objects.filter(username__in=['guia1', 'guia2'])
        tourists = User.objects.filter(username__in=['turista1', 'turista2'])
        self.assertEqual(guides.count(), 2)
        self.assertEqual(tourists.count(), 2)
        for guide in guides:
            self.assertEqual(Experience.objects.filter(creator=guide).count(), 4)
        for tourist in tourists:
            self.assertEqual(Reservation.objects.filter(user=tourist).count(), 3)
        self.assertIn('Datos de demostración listos.', output.getvalue())
