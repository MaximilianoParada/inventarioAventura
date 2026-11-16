from django.test import TestCase
from django.urls import reverse

from cuentas.models import Role, User, UserRole


class StaffUserManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_role, _ = Role.objects.update_or_create(
            role_name=Role.ADMINISTRATOR,
            defaults={'administrador': 2, 'guia': 0, 'operador': 0, 'turista': 0, 'cliente': 0},
        )
        cls.rol_guia, _ = Role.objects.update_or_create(
            role_name=Role.GUIA_OPERADOR,
            defaults={'administrador': 0, 'guia': 2, 'operador': 2, 'turista': 0, 'cliente': 0},
        )
        cls.admin = User.objects.create_superuser(
            username='admin-test',
            email='admin@example.test',
            password='test-password-123!',
        )
        UserRole.objects.create(user_id=cls.admin, role=cls.admin_role)

    def test_admin_can_create_user_and_assign_role(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('user_create')).status_code, 200)

        response = self.client.post(
            reverse('user_create'),
            {
                'username': 'guia-creado',
                'email': 'guia@example.test',
                'first_name': 'Test',
                'last_name': 'Operador',
                'role': Role.GUIA_OPERADOR,
                'password1': 'Safe-test-password-123!',
                'password2': 'Safe-test-password-123!',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='guia-creado')
        self.assertTrue(user.check_password('Safe-test-password-123!'))
        self.assertTrue(
            UserRole.objects.filter(user_id=user, role=self.rol_guia).exists()
        )

    def test_login_and_post_logout_manage_the_authentication_session(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        response = self.client.post(
            reverse('login'),
            {'username': self.admin.username, 'password': 'test-password-123!'},
        )
        self.assertRedirects(response, reverse('dashboard'))
        self.assertIn('_auth_user_id', self.client.session)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)
