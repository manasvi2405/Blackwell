from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('shop/<cat>',views.shop,name='shop'),
    path('product/<id>/',views.product,name='product'),
    path('shopbycategory/<cat>',views.shopbycategory,name='shopbycategory'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/',views.checkout_view,name='checkout'),
   path('add_to_cart/<item_id>', views.add_to_cart, name='add_to_cart'),
   path('update_cart_quantity/<str:action>/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
   path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
   path('process_order/',views.process_order,name='process_order'),
   path('payment/verify/', views.payment_verify, name='payment_verify'),
   path('payment_page/<order_id>',views.payment_page,name='payment_page'),
   path('cancel_order/<order_id>',views.cancel_order,name='cancel_order'),
]