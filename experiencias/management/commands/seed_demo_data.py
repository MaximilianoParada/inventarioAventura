import secrets
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from cuentas.models import Role, UserRole
from experiencias.models import Category, Experience, Reservation


class Command(BaseCommand):
    help = 'Crea cuentas y datos de prueba para los tres roles del sistema.'

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        role_admin, _ = Role.objects.update_or_create(
            role_name=Role.ADMINISTRATOR,
            defaults={'administrador': 2, 'guia': 0, 'operador': 0, 'turista': 0, 'cliente': 0},
        )
        role_guide, _ = Role.objects.update_or_create(
            role_name=Role.GUIDE_OPERATOR,
            defaults={'administrador': 0, 'guia': 2, 'operador': 2, 'turista': 0, 'cliente': 0},
        )
        role_tourist, _ = Role.objects.update_or_create(
            role_name=Role.TOURIST_CLIENT,
            defaults={'administrador': 0, 'guia': 0, 'operador': 0, 'turista': 2, 'cliente': 2},
        )

        credentials = []
        admin, password = self._ensure_user(
            User,
            'admin_demo',
            'admin-demo@aventuras.local',
            role_admin,
            is_superuser=True,
        )
        if password:
            credentials.append(('Administrador', admin.username, password))

        guides = []
        for username in ('guia1', 'guia2'):
            guide, password = self._ensure_user(
                User, username, f'{username}@aventuras.local', role_guide
            )
            guides.append(guide)
            if password:
                credentials.append(('Guía / Operador', guide.username, password))

        tourists = []
        for username in ('turista1', 'turista2'):
            tourist, password = self._ensure_user(
                User, username, f'{username}@aventuras.local', role_tourist
            )
            tourists.append(tourist)
            if password:
                credentials.append(('Turista / Cliente', tourist.username, password))

        categories = self._ensure_categories()
        guide_experiences = [
            self._ensure_experiences(guides[0], categories, 'Cordillera'),
            self._ensure_experiences(guides[1], categories, 'Aventura'),
        ]

        for tourist, experiences in zip(tourists, guide_experiences):
            for experience in experiences[:3]:
                Reservation.objects.get_or_create(
                    user=tourist,
                    experience=experience,
                    defaults={'payment_status': Reservation.PAYMENT_PENDING},
                )

        self.stdout.write(self.style.SUCCESS('Datos de demostración listos.'))
        if credentials:
            self.stdout.write('Guarda estas contraseñas; no se volverán a mostrar:')
            for role_name, username, password in credentials:
                self.stdout.write(f'{role_name}: {username} / {password}')
        else:
            self.stdout.write(
                'Las cuentas de demostración ya existían; sus contraseñas no fueron modificadas.'
            )
        self.stdout.write('Administrador de demostración: admin_demo')
        self.stdout.write('Guías: guia1, guia2; turistas: turista1, turista2')

    def _ensure_user(self, User, username, email, role, is_superuser=False):
        user = User.objects.filter(username=username).first()
        password = None
        if user is None:
            password = secrets.token_urlsafe(18)
            extra_fields = {'email': email, 'is_active': True}
            if is_superuser:
                extra_fields.update({'is_staff': True, 'is_superuser': True})
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                )
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    **extra_fields,
                )
        else:
            changed_fields = []
            if not user.is_active:
                user.is_active = True
                changed_fields.append('is_active')
            if is_superuser:
                if not user.is_staff:
                    user.is_staff = True
                    changed_fields.append('is_staff')
                if not user.is_superuser:
                    user.is_superuser = True
                    changed_fields.append('is_superuser')
            if changed_fields:
                user.save(update_fields=changed_fields)

        UserRole.objects.get_or_create(user_id=user, role=role)
        return user, password

    def _ensure_categories(self):
        category_descriptions = {
            'Trekking': 'Recorridos guiados por senderos y paisajes naturales.',
            'Canopy': 'Circuitos de aventura entre las copas de los árboles.',
            'Arriendo de equipos': 'Equipos para disfrutar actividades al aire libre.',
            'Kayak': 'Experiencias de navegación y exploración en kayak.',
        }
        return {
            name: Category.objects.update_or_create(
                name=name,
                defaults={'description': description, 'is_active': True},
            )[0]
            for name, description in category_descriptions.items()
        }

    def _ensure_experiences(self, guide, categories, series):
        titles = [
            f'{series}: Trekking de montaña',
            f'{series}: Circuito canopy',
            f'{series}: Jornada de kayak',
            f'{series}: Arriendo de equipo outdoor',
        ]
        experiences = []
        for index, title in enumerate(titles):
            experience, created = Experience.objects.get_or_create(
                title=title,
                creator=guide,
                defaults={
                    'description': f'Experiencia de demostración: {title}.',
                    'price': Decimal('15000.00') + Decimal(index * 2500),
                    'capacity': 12,
                    'scheduled_at': timezone.now() + timedelta(days=30 + index),
                    'category': list(categories.values())[index],
                    'is_active': True,
                },
            )
            if not created:
                changed_fields = []
                if experience.scheduled_at <= timezone.now():
                    experience.scheduled_at = timezone.now() + timedelta(days=30 + index)
                    changed_fields.append('scheduled_at')
                if not experience.is_active:
                    experience.is_active = True
                    changed_fields.append('is_active')
                if changed_fields:
                    experience.save(update_fields=changed_fields)
            experiences.append(experience)
        return experiences
