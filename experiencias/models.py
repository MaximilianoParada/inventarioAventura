from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        db_table = 'category'
        ordering = ['name']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.name


class Experience(models.Model):
    title = models.CharField(max_length=150, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Precio',
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cupo máximo',
    )
    scheduled_at = models.DateTimeField(verbose_name='Fecha y hora')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='experiences',
        verbose_name='Categoría',
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_experiences',
        verbose_name='Creada por',
    )
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'experience'
        ordering = ['scheduled_at', 'title']
        verbose_name = 'Experiencia'
        verbose_name_plural = 'Experiencias'

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.scheduled_at and self.scheduled_at <= timezone.now():
            from django.core.exceptions import ValidationError

            raise ValidationError({'scheduled_at': 'La fecha de la experiencia debe ser futura.'})

    @property
    def available_places(self):
        reserved = getattr(self, 'reservation_count', None)
        if reserved is None:
            reserved = self.reservations.count()
        return max(self.capacity - reserved, 0)


class Reservation(models.Model):
    PAYMENT_PENDING = 'pending'
    PAYMENT_CONFIRMED = 'confirmed'
    PAYMENT_CHOICES = [
        (PAYMENT_PENDING, 'Pendiente'),
        (PAYMENT_CONFIRMED, 'Confirmado'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Turista',
    )
    experience = models.ForeignKey(
        Experience,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Experiencia',
    )
    reserved_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inscripción')
    payment_status = models.CharField(
        max_length=12,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_PENDING,
        verbose_name='Estado de pago',
    )

    class Meta:
        db_table = 'reservation'
        ordering = ['-reserved_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'experience'],
                name='unique_user_experience_reservation',
            ),
        ]
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f'{self.user.username} - {self.experience.title}'
