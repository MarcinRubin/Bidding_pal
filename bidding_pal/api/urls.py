from django.urls import path
from rest_framework import routers
from .views import DealViewSet, BidViewSet, GetCSRFToken

router = routers.DefaultRouter()
router.register(r"deals", DealViewSet)
router.register(r"bids", BidViewSet)

urlpatterns = [
    path("get_csrf_token/", GetCSRFToken.as_view(), name="get_csrf_token")
]

urlpatterns += router.urls
