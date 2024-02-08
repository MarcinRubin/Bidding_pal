from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from .models import Deal, Bid
from .serializers import DealSerializer, BidSerializer, BidSerializerAdd
from .utils import create_tree


class DealViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer

    @action(detail=True)
    def get_bids_tree(self, request, pk=None):
        bids = self.queryset.get(id=pk).bids.all()
        data = create_tree(bids)
        return Response({"bids": data}, status.HTTP_200_OK)


class BidViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
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
