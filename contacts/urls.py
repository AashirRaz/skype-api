# contacts/urls.py
from django.urls import path
from .views import get_skype_contacts, send_skype_message

urlpatterns = [
    path('get-contacts/', get_skype_contacts, name='get_skype_contacts'),
    path('send-skype-message/', send_skype_message, name='send_skype_message'),
]