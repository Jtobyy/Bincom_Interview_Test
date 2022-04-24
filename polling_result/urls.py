from django.urls import path
from . import views

app_name = 'polling_result'

urlpatterns = [
    path('', views.individual_polling_result, name="home"),    
    path('individual_polling_result', views.individual_polling_result, name="individual_polling_result"),
    path('total_result', views.summed_total_result, name="total_result"),
    path('total_result/<int:lga_id>', views.summed_total_result, name="total_result"),
    path('new_result', views.new_result, name="new_result"),
]