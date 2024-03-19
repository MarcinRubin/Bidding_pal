from django.core.management.base import BaseCommand
from api.models import Deal, Bid, BidClosure
from django.db.utils import DataError


class Command(BaseCommand):
    help = "Add data to database"

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str,
                            help='Name of the directory in data sets folder')
        parser.add_argument('category', type=str,
                            help='Category of the deal set')

    def handle(self, *args, **kwargs):
        def extract_hand(path):
            with open(path, 'r') as file:
                deals = []
                buffer = ""
                for x in file:
                    if x == "\n":
                        deals.append(buffer[:-1])
                        buffer = ""
                        continue

                    if x == "-\n":
                        x = "\n"

                    buffer += f"{x[:-1].replace(' ', '')}."
                deals.append(buffer[:-1])
            return deals

        def bid_sequence_save(bidding_list, deal_object):
            first_bid = bidding_list.pop(0)
            player = "W"
            root_bid = Bid.objects.create(name=first_bid, deal=deal_object,
                                          comment="", player=player)

            BidClosure.objects.create(ancestor=root_bid, descendant=root_bid, depth=0)
            for bid in bidding_list:
                player = "E" if player == "W" else "W"
                current_bid = Bid.objects.create(name=bid, deal=deal_object,
                                                 comment="", player=player)
                BidClosure.objects.create(ancestor=current_bid, descendant=current_bid,
                                          depth=0)
                list_of_ancestors = BidClosure.objects.filter(descendant=root_bid)
                for ancestor in list_of_ancestors:
                    BidClosure.objects.create(ancestor=ancestor.ancestor,
                                              descendant=current_bid,
                                              depth=ancestor.depth + 1)
                root_bid = current_bid

        dir = kwargs['directory']
        category = kwargs['category']
        self.stdout.write("Adding new data to database")

        with open(f"data_sets/{dir}/answers.csv", "r") as answers:
            biddings = []
            for line in answers:
                biddings.append(line.replace("\n", "").split(","))
            e_hands = extract_hand(f"data_sets/{dir}/E.csv")
            w_hands = extract_hand(f"data_sets/{dir}/W.csv")
            self.stdout.write("Answers and hands extracted")

        for i in range(len(biddings)):
            try:
                deal = Deal.objects.create(e=e_hands[i], w=w_hands[i], player="W",
                                       comment=f"{category} - {i + 1}",
                                       category=category)
                bid_sequence_save(biddings[i], deal)
            except DataError:
                self.stdout.write(f"Probably incorrect number of card in hand-{i+1}")

        self.stdout.write("data added")
