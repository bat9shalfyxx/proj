# main/backends.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
import re

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        UserModel = get_user_model()
        
        try:
            # Сначала пробуем найти по email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                # Если не нашли по email, пробуем по номеру телефона
                # Нормализуем номер телефона
                phone = self.normalize_phone(username)
                user = UserModel.objects.get(phone_number=phone)
            except (UserModel.DoesNotExist, ValueError):
                return None
        
        if user.check_password(password):
            return user
        return None
    
    def normalize_phone(self, phone):
        """Нормализует номер телефона к формату +7XXXXXXXXXX"""
        phone = re.sub(r'[^\d+]', '', phone)
        if not phone.startswith('+7'):
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
            elif phone.startswith('7'):
                phone = '+' + phone
            else:
                phone = '+7' + phone
        
        if len(phone) != 12:
            raise ValueError('Invalid phone number length')
        
        return phone