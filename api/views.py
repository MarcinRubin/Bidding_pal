from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from .models import Deal, Bid
from .serializers import DealSerializer, BidSerializer, BidSerializerAdd, \
    DealSerializerWithPaths, DealSerializerForQuiz
from .utils import create_tree, get_paths
from django.views.decorators.csrf import ensure_csrf_cookie
from random import sample, randint


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFToken(APIView):

    def get(self, request):
        return Response({"success": "CSRF token set"})


class DealViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    filterset_fields = {
        'category': ["in", "exact"],
    }

    def get_serializer_class(self):
        if self.action == "get_all_paths":
            return DealSerializerWithPaths
        if self.action == "get_quiz_element":
            return DealSerializerForQuiz
        return super().get_serializer_class()

    @action(detail=True, methods=["GET"])
    def get_all_paths(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def get_bids_tree(self, request, pk=None):
        bids = self.get_queryset().get(id=pk).bids.all()
        data = create_tree(bids)
        return Response({"bids": data}, status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def get_categories(self, request):
        categories = list(Deal.objects.values_list("category", flat=True).distinct())
        return Response({"categories": categories}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def get_quiz_element(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        random_deal = sample(list(queryset), 1)[0]
        path = get_paths(random_deal.bids.all())[0]

        random_idx = randint(0, len(path) - 1)
        answer = path[random_idx]
        question = [*path[0:random_idx], {"bid": "?", "player": answer["player"]}]

        deal_serializer = self.get_serializer(random_deal)
        return Response({
            "deal": deal_serializer.data,
            "path": question,
            "answer": [answer]
        },
            status.HTTP_200_OK
        )


class BidViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer

    def get_serializer_class(self):
        if self.action == "add_bid":
            return BidSerializerAdd
        return super().get_serializer_class()

    @action(detail=True)
    def get_next_bids(self, request, pk=None):
        next_bids = self.get_queryset().filter(closure_descendants__ancestor_id=pk,
                                               closure_descendants__depth=1)
        serializer = self.get_serializer(next_bids, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def add_bid(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(bid_id=pk)
        return Response(serializer.data, status.HTTP_201_CREATED)

    @action(detail=True)
    def get_history(self, request, pk=None):
        history = self.get_queryset().filter(
            closure_ancestor__descendant_id=pk).order_by("-closure_ancestor__depth")
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
