import hashlib
import hmac
import json
import requests
from django.conf import settings
from datetime import datetime

class PayUClient:
    def __init__(self):
        self.api_key = settings.PAYU_API_KEY
        self.merchant_id = settings.PAYU_MERCHANT_ID
        self.account_id = settings.PAYU_ACCOUNT_ID
        self.base_url = "https://api.payulatam.com" if settings.DEBUG else "https://api.payulatam.com"
        
    def create_signature(self, reference, amount, currency):
        """Crea firma para PayU"""
        signature_string = f"{self.api_key}~{self.merchant_id}~{reference}~{amount}~{currency}"
        return hashlib.md5(signature_string.encode()).hexdigest()
    
    def create_payment(self, subscription, user, ip_address):
        """Crea pago en PayU"""
        reference = f"SUB-{subscription.id}-{datetime.now().timestamp()}"
        amount = self.get_plan_price(subscription.plan)
        
        payload = {
            "language": "es",
            "command": "SUBMIT_TRANSACTION",
            "merchant": {
                "apiKey": self.api_key,
                "apiLogin": settings.PAYU_API_LOGIN
            },
            "transaction": {
                "order": {
                    "accountId": self.account_id,
                    "referenceCode": reference,
                    "description": f"Suscripción {subscription.get_plan_display()}",
                    "language": "es",
                    "signature": self.create_signature(reference, amount, "COP"),
                    "notifyUrl": f"{settings.BASE_URL}/billing/payu/webhook/",
                    "additionalValues": {
                        "TX_VALUE": {"value": amount, "currency": "COP"}
                    },
                    "buyer": {
                        "fullName": user.get_full_name() or user.username,
                        "emailAddress": user.email,
                        "shippingAddress": {
                            "street1": "NA",
                            "city": "NA",
                            "country": "CO"
                        }
                    }
                },
                "type": "AUTHORIZATION_AND_CAPTURE",
                "paymentMethod": "VISA",
                "paymentCountry": "CO",
                "ipAddress": ip_address,
                "cookie": "cookie_" + reference,
                "userAgent": "Mozilla/5.0"
            },
            "test": settings.DEBUG
        }
        
        response = requests.post(
            f"{self.base_url}/payments-api/4.0/service.cgi",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        return response.json(), reference
    
    def get_plan_price(self, plan):
        """Retorna precio según plan"""
        prices = {
            "FREE": 0,
            "PRO": 19900,
            "BUSINESS": 49900
        }
        return prices.get(plan, 0)