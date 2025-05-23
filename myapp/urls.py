from django.urls import path, include
from . import views
from .views import MyClass1
from .views import MyClass2View
from .views import signup_view, login_view, logout_view, profile_redirect_view


urlpatterns = [
    path('', views.mypage2, name = 'mypage2'),
    path('mysubdir1/', views.mysubdir1, name='mysubdir1'),
    path('mypage3', views.mypage3, name='mypage3'),
    path('mypage4', MyClass1.as_view(), name='mypage4'),
    path('mypage5', MyClass2View.as_view(), name = 'mypage5'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup_view, name = 'signup'),
    path('accounts/login/', login_view, name = 'login'),
    path('accounts/logout/', logout_view, name = 'logout'),
    path('accounts/profile/', profile_redirect_view, name='profile_redirect'),
    path('home/', views.doctor_home_view, name='home_doctor'),
    path('home_user/', views.patient_home_view, name='home_user'), 
    path('nowy_pacjent/', views.mypage3, name='nowy_pacjent'),
    path('profil_pacjenta/<int:pk>/', views.patient_profile, name='profil_pacjenta'),   #przekazać do url z home_doctor
    path('chart-data/<int:badanie_id>/', views.chart_data, name='chart_data'),
    path('wizyta/<int:pk>/delete/', views.delete_wizyta, name='delete_wizyta'),
    path('wizyta/<int:pk>/edit/', views.edit_wizyta, name='edit_wizyta'),
    path('badanie/<int:pk>/delete/', views.delete_badanie, name='delete_badanie'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('generate-csv/', views.generate_csv, name='generate_csv'),


] 


