from rest_framework import routers
from WebService import views
from django.conf.urls import url, include
from django.urls import path


router = routers.DefaultRouter()
router.register(r'users', views.usersViewSet, base_name='users')
router.register(r'performances', views.performanceViewSet, base_name='performances')
router.register(r'tickets', views.ticketViewSet, base_name='tickets')
router.register(r'unusedTickets', views.unusedTicketViewSet, base_name='unusedtickets')
router.register(r'cafeteriaVouchers', views.cafeteriaVoucherViewSet, base_name='cafeteriaVouchers')
router.register(r'unusedCafeteriaVouchers', views.unusedCafeteriaVoucherViewSet, base_name='unusedCafeteriaVouchers')
router.register(r'cafeteriaOrders', views.cafeteriaOrderViewSet, base_name='cafeteriaOrders')
router.register(r'unpaidCafeteriaOrders', views.unpaidCafeteriaOrderViewSet, base_name='unpaidCafeteriaOrders')






urlpatterns = [
	url(r'^', include(router.urls)),
	path('login/', views.login),
	path('buyTickets', views.buyPerformanceTickets),
	path('validateTickets', views.validateTickets),
	path('payCafeteriaOrder', views.payCafeteriaOrder)
]
