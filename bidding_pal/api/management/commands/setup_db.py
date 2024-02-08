from django.core.management.base import BaseCommand
from api.models import Deal, Bid, BidClosure


class Command(BaseCommand):
    help = "Generate database from input files"

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str,
                            help='Name of the directory in data sets folder')

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
            root_bid = Bid.objects.create(name=first_bid, deal=deal_object, comment="")

            BidClosure.objects.create(ancestor=root_bid, descendant=root_bid, depth=0)
            for bid in bidding_list:
                current_bid = Bid.objects.create(name=bid, deal=deal_object, comment="")
                BidClosure.objects.create(ancestor=current_bid, descendant=current_bid,
                                          depth=0)
                list_of_ancestors = BidClosure.objects.filter(descendant=root_bid)
                for ancestor in list_of_ancestors:
                    BidClosure.objects.create(ancestor=ancestor.ancestor,
                                              descendant=current_bid,
                                              depth=ancestor.depth + 1)
                root_bid = current_bid

        dir = kwargs['directory']
        self.stdout.write("Deleting old data...")
        models = [Bid, BidClosure, Deal]
        for m in models:
            m.objects.all().delete()
        self.stdout.write("Creating new database...")

        with open(f"data_sets/{dir}/answers.csv", "r") as answers:
            biddings = []
            for line in answers:
                biddings.append(line.replace("\n", "").split(","))
            e_hands = extract_hand(f"data_sets/{dir}/E.csv")
            w_hands = extract_hand(f"data_sets/{dir}/W.csv")
            self.stdout.write("Answers and hands extracted")

        for i in range(len(biddings)):
            deal = Deal.objects.create(e=e_hands[i], w=w_hands[i], player="E",
                                       comment=f"{dir} - Rozdanie nr. {i + 1}")
            bid_sequence_save(biddings[i], deal)

        self.stdout.write("done")
