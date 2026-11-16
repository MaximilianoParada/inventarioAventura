from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    
    USERNAME_FIELD = 'username'
    
    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
class Role(models.Model):
    ADMINISTRATOR = 'Administrador'
    GUIDE_OPERATOR = 'Guía / Operador'
    TOURIST_CLIENT = 'Turista / Cliente'

    PERMISSION_CHOICES = [
        (0, 'No Access'),
        (1, 'view only'),
        (2, 'create and modify')
    ]
    
    role_name = models.CharField(max_length=50, primary_key=True)
    administrador = models.IntegerField(choices=PERMISSION_CHOICES, default=0)
    guia = models.IntegerField(choices=PERMISSION_CHOICES, default=0)
    operador = models.IntegerField(choices=PERMISSION_CHOICES, default=0)
    turista = models.IntegerField(choices=PERMISSION_CHOICES, default=0)
    cliente = models.IntegerField(choices=PERMISSION_CHOICES, default=0)
    
    class Meta:
        db_table = 'role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        
    def __str__(self):
        return self.role_name
    
class UserRole(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'user_role'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        unique_together = ('user_id', 'role')
        
    def __str__(self):
        return f"{self.user_id.username} - {self.role.role_name}"