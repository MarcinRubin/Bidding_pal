from .models import Deal, Bid, BidClosure
from rest_framework import serializers
from .utils import get_paths


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = "__all__"


class DealSerializerWithPaths(DealSerializer):
    paths = serializers.SerializerMethodField(read_only=True)

    def get_paths(self, instance):
        bids = instance.bids.all()
        return get_paths(bids)


class DealSerializerForQuiz(DealSerializer):
    class Meta(DealSerializer.Meta):
        fields = ("id", "e", "w", "player")


class BidSerializer(serializers.ModelSerializer):
    deal = DealSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = "__all__"


class BidSerializerWithoutDeal(BidSerializer):
    class Meta(BidSerializer.Meta):
        fields = ("name", "comment")


class BidSerializerAdd(BidSerializer):
    class Meta(BidSerializer.Meta):
        fields = ("name", "comment")

    def create(self, validated_data, **kwargs):
        bid_id = validated_data.pop("bid_id")
        previous_bids = BidClosure.objects.filter(descendant__id=bid_id).order_by("depth")
        validated_data.update({"deal": previous_bids[0].ancestor.deal})
        new_bid = Bid.objects.create(**validated_data)
        BidClosure.objects.create(ancestor=new_bid,
                                  descendant=new_bid,
                                  depth=0)
        for closure in previous_bids:
            BidClosure.objects.create(ancestor=closure.ancestor,
                                      descendant=new_bid,
                                      depth=closure.depth + 1)

        return previous_bids[0]
