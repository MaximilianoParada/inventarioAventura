from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cuentas.models import Role, User, UserRole
from experiencias.models import Category, Experience


class PublicAndDashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol_guia, _ = Role.objects.update_or_create(
            role_name=Role.GUIA_OPERADOR,
            defaults={'administrador': 0, 'guia': 2, 'operador': 2, 'turista': 0, 'cliente': 0},
        )
        cls.guia = User.objects.create_user(
            username='guia-dashboard',
            password='test-password-123!',
        )
        UserRole.objects.create(user_id=cls.guia, role=cls.rol_guia)
        category = Category.objects.create(name='Kayak')
        Experience.objects.create(
            title='Kayak público',
            description='Salida guiada',
            price=Decimal('12000.00'),
            capacity=8,
            scheduled_at=timezone.now() + timedelta(days=5),
            category=category,
            creator=cls.guia,
        )

    def test_home_displays_public_catalogue_link_and_experience(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aventuras del Sur')
        self.assertContains(response, 'Kayak público')
        self.assertContains(response, reverse('catalog'))

    def test_dashboard_uses_role_context_and_sb_admin_template(self):
        self.client.force_login(self.guia)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Guía / Operador')
        self.assertContains(response, 'Mis experiencias')
        self.assertContains(response, 'sb-admin-2.min.css')
