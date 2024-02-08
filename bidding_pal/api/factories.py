from factory.django import DjangoModelFactory
from factory import SubFactory, Faker
from models import Bid, BidClosure, Deal


# Defining a factory
class DealFactory(DjangoModelFactory):
    class Meta:
        model = Deal


class BidFactory(DjangoModelFactory):
    class Meta:
        model = Bid

    name = Sequence(lambda n: 'Team%s' % n)
    league = SubFactory(LeagueFactory)


class BidClosureFactory(DjangoModelFactory):
    league = SubFactory(LeagueFactory)
    home = SubFactory(TeamFactory)
    away = SubFactory(TeamFactory)
    home_points = 1
    away_points = 1
    scheduled = Faker('date_time', tzinfo=timezone.get_current_timezone())

    class Meta:
        model = BidClosure
