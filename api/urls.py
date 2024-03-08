from django.urls import path
from rest_framework import routers
from .views import DealViewSet, BidViewSet, GetCSRFToken, GetQuizElement

router = routers.DefaultRouter()
router.register(r"deals", DealViewSet)
router.register(r"bids", BidViewSet)

urlpatterns = [
    path("get_csrf_token/", GetCSRFToken.as_view(), name="get_csrf_token"),
    path("get_quiz_deal/", GetQuizElement.as_view(), name='get-quiz-element')
]

urlpatterns += router.urls
