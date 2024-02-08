from .models import Deal, Bid, BidClosure
from rest_framework import serializers


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = "__all__"


class BidSerializer(serializers.ModelSerializer):
    deal = DealSerializer()

    class Meta:
        model = Bid
        fields = "__all__"


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
                                      depth=closure.depth+1)

        return previous_bids[0]

