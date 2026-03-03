from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from .models import FinancialOperation, AuditLog, User

@login_required
def dashboard_view(request):
    # Cálculo em tempo real (Nunca armazenado)
    qs = FinancialOperation.objects.filter(status='COMPLETED')
    credits = qs.filter(type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or 0
    debits = qs.filter(type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = credits - debits

    total_ops = FinancialOperation.objects.count()
    reversals = FinancialOperation.objects.filter(status='REVERSED').count()
    reversal_rate = (reversals / total_ops * 100) if total_ops > 0 else 0

    context = {
        'credits': float(credits), 'debits': float(debits),
        'balance': float(balance), 'reversal_rate': float(reversal_rate)
    }
    return render(request, 'dashboard.html', context)

@login_required
def operations_view(request):
    if request.method == 'POST':
        # Busca a instância real do usuário para evitar problemas de UUID/String no SQLite
        real_user = User.objects.get(pk=request.user.pk)

        # Criação Atômica com AuditLog
        with transaction.atomic():
            op = FinancialOperation.objects.create(
                type=request.POST.get('type'),
                amount=request.POST.get('amount'),
                description=request.POST.get('description'),
                user=real_user
            )
            AuditLog.objects.create(
                operation=op, 
                action='CREATED',
                new_value={'amount': str(op.amount), 'type': op.type},
                performed_by=real_user
            )
            messages.success(request, 'Operação registrada com sucesso!')
            return redirect('operations')

    operations = FinancialOperation.objects.select_related('user').order_by('-created_at')
    return render(request, 'operations.html', {'operations': operations})

@login_required
def reverse_operation(request, op_id):
    if request.method != 'POST': # Bloqueia acesso via URL (GET) e DELETE
        return redirect('operations')
        
    if request.user.role != 'ADMIN':
        messages.error(request, 'Apenas ADMIN pode estornar operações.')
        return redirect('operations')

    op = get_object_or_404(FinancialOperation, id=op_id)
    
    if op.status == 'REVERSED':
        messages.warning(request, 'Operação já estornada.')
        return redirect('operations')

    # Busca a instância real do usuário
    real_user = User.objects.get(pk=request.user.pk)

    # Estorno Atômico
    with transaction.atomic():
        op.status = 'REVERSED'
        op.save()
        AuditLog.objects.create(
            operation=op, action='REVERSED',
            old_value={'status': 'COMPLETED'}, new_value={'status': 'REVERSED'},
            performed_by=real_user
        )
        messages.success(request, 'Operação estornada com sucesso.')
        
    return redirect('operations')