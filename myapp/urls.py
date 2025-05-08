from django.urls import path
from . import views
from .views import MyClass1
from .views import MyClass2View

urlpatterns = [
    path('', views.mypage2, name = 'mypage2'),
    path('mysubdir1/', views.mysubdir1, name='mysubdir1'),
    path('mypage3', views.mypage3, name='mypage3'),
    path('mypage4', MyClass1.as_view(), name='mypage4'),
    path('mypage5', MyClass2View.as_view(), name = 'mypage5'),
]

