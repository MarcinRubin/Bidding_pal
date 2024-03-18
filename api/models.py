from django.db import models


class Deal(models.Model):
    e = models.CharField(max_length=16)
    w = models.CharField(max_length=16)
    player = models.CharField(max_length=1, default="N")
    comment = models.TextField(max_length=100, default="")
    category = models.CharField(max_length=100, default="")


class Bid(models.Model):
    name = models.CharField(max_length=4, default="")
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="bids")
    comment = models.TextField(blank=True)
    player = models.CharField(max_length=1, default="")


class BidClosure(models.Model):
    ancestor = models.ForeignKey(Bid, on_delete=models.CASCADE,
                                 related_name="closure_ancestor")
    descendant = models.ForeignKey(Bid, on_delete=models.CASCADE,
                                   related_name="closure_descendants")
    depth = models.IntegerField()

    def __str__(self):
        return f"{self.ancestor}, {self.descendant}"
