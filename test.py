
with open("data_sets/1H/E.csv", 'r') as file:
    deal_n = []
    buffer = ""
    for x in file:
        if x == "\n":
            deal_n.append(buffer[:-1])
            buffer = ""
            continue

        if x == "-\n":
            x = "\n"

        buffer += f"{x[:-1].replace(' ', '')}."
    deal_n.append(buffer[:-1])

print(deal_n)
