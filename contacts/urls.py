# contacts/urls.py
from django.urls import path
from .views import get_skype_contacts

urlpatterns = [
    path('get-contacts/', get_skype_contacts, name='get_skype_contacts'),
]