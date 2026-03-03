from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (('ADMIN', 'Admin'), ('OPERATOR', 'Operator'))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='OPERATOR')


    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="core_user_set"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="core_user_permissions_set"
    )

class FinancialOperation(models.Model):
    TYPE_CHOICES = (('CREDIT', 'Credit'), ('DEBIT', 'Debit'))
    STATUS_CHOICES = (('COMPLETED', 'Completed'), ('REVERSED', 'Reversed'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='COMPLETED')
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='operations')

class AuditLog(models.Model):
    ACTION_CHOICES = (('CREATED', 'Created'), ('REVERSED', 'Reversed'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operation = models.ForeignKey(FinancialOperation, on_delete=models.RESTRICT)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField()
    performed_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    timestamp = models.DateTimeField(default=timezone.now)