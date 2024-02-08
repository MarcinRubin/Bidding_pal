from django.contrib import admin

from .models import Deal, Bid, BidClosure

admin.site.register(Deal)
admin.site.register(Bid)
admin.site.register(BidClosure)
