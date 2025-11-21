

from django.urls import include, path
from .views import  CartItemView, ClearCartView, GroupsDeliveryViewSet, GroupsManagerViewSet, MenuItemModView, MenuItemView, UserMeView, UserModView, UserView,LoginView
from rest_framework.routers import SimpleRouter
from .views import OrderViewSet

router = SimpleRouter()
router.register('orders', OrderViewSet)
router.register('groups/manager/users', GroupsManagerViewSet, basename="manager")
router.register('groups/delivery/users', GroupsDeliveryViewSet, basename="delivery")


urlpatterns = [
    
    path('menu-items/', MenuItemView.as_view()),
    path('users/', UserView.as_view()),
    path('users/<int:pk>/', UserModView.as_view()),
    path('menu-item/<int:pk>/',MenuItemModView.as_view()),
    path('users/me/', UserMeView.as_view()),
    path('cart/menu-items/', CartItemView.as_view()),
    path('cart/delete/', ClearCartView.as_view()),
    path('', include(router.urls)),
]