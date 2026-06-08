from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('',views.EditAccount.as_view(),name='dashboard'),
    path('accounts/',include("django.contrib.auth.urls")),
    path('register/',views.SignUp.as_view(),name='register'),
    path('addaddress/',views.add_address.as_view(),name='addaddress'),
    path('listaddress/',views.list_address.as_view(),name='listaddress'),
    path('deleteaddress/<pk>',views.delete_address.as_view(),name='deleteaddress'),
    path('updateaddress/<pk>',views.update_address.as_view(),name='updateaddress'),
    path('editprofile/',views.EditProfile.as_view(),name='editprofile'),
    path('order_history/',views.order_history,name='order_history'),
    path('track/',views.track_order,name='track_order'),
]