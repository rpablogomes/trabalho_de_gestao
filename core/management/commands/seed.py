from django.core.management.base import BaseCommand
from core.models import User, FinancialOperation, AuditLog
from decimal import Decimal

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # 1. Limpa o banco na ordem certa
        AuditLog.objects.all().delete()
        FinancialOperation.objects.all().delete()
        User.objects.all().delete()
        
        # 2. Criação do ADMIN usando o método nativo seguro
        admin = User.objects.create_superuser(
            username='admin@finaudit.com',
            email='admin@finaudit.com',
            password='admin123',
            name='Admin User',
            role='ADMIN'
        )
        
        # 3. Criação do OPERADOR usando o método nativo seguro
        op = User.objects.create_user(
            username='operator@finaudit.com',
            email='operator@finaudit.com',
            password='op123',
            name='Operator User',
            role='OPERATOR'
        )
        
        # 4. Operação inicial
        op1 = FinancialOperation.objects.create(
            type='CREDIT', amount=Decimal('1000.00'), description='Aporte Inicial', user=admin
        )
        AuditLog.objects.create(
            operation=op1, action='CREATED', new_value={'amount': '1000'}, performed_by=admin
        )
        
        self.stdout.write(self.style.SUCCESS('Seed concluído! Senhas criptografadas corretamente pelo Django.'))