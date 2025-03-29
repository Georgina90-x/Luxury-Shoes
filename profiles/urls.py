from django.urls import path
from . import views
from .views import send_marketing_email

urlpatterns = [
    path('', views.profile, name='profile'),
    path(
        'order_history/<order_number>',
        views.order_history, name='order_history'
        ),
    path('send-marketing-email/', send_marketing_email,
         name='send_marketing_email'),
]
