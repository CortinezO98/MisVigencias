from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Subscription, Payment
from .payu_client import PayUClient
import json

@login_required
def create_payment(request):
    """Inicia pago en PayU"""
    subscription = request.user.subscription
    payu = PayUClient()
    
    # Si ya es PRO, redirigir
    if subscription.plan != "FREE":
        return redirect('dashboard')
    
    response, reference = payu.create_payment(
        subscription=subscription,
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    if response.get('code') == 'SUCCESS':
        # Guardar transacción pendiente
        Payment.objects.create(
            subscription=subscription,
            amount=payu.get_plan_price("PRO"),
            currency="COP",
            status="PENDING",
            transaction_id=reference,
            payment_method="PAYU",
            description="Actualización a PRO"
        )
        
        # Redirigir a PayU
        return redirect(response['transactionResponse']['transactionResponse']['extraParameters']['PAGO_PAYU_URL'])
    
    return render(request, 'billing/payment_error.html', {'error': response})

@csrf_exempt
def payu_webhook(request):
    """Webhook de confirmación de PayU"""
    if request.method == 'POST':
        data = json.loads(request.body)
        transaction = data.get('transaction')
        
        if transaction.get('state') == 'APPROVED':
            # Actualizar pago
            payment = Payment.objects.filter(
                transaction_id=transaction['referenceCode']
            ).first()
            
            if payment:
                payment.status = 'COMPLETED'
                payment.save()
                
                # Actualizar suscripción
                subscription = payment.subscription
                subscription.plan = 'PRO'
                subscription.status = 'ACTIVE'
                subscription.payment_method = 'PAYU'
                subscription.save()
        
        return JsonResponse({'status': 'ok'})
    
    return JsonResponse({'error': 'Invalid method'}, status=400)