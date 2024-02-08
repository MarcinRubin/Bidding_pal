from rest_framework import routers
from .views import DealViewSet, BidViewSet

router = routers.DefaultRouter()
router.register(r"deals", DealViewSet)
router.register(r"bids", BidViewSet)

urlpatterns = [
]

urlpatterns += router.urls
