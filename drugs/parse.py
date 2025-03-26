import requests
import json
import pandas as pd


def get_equivalent(curie):
    nodenorm=f"https://nodenormalization-sri.renci.org/1.5/get_normalized_nodes?curie={curie}&conflate=true&drug_chemical_conflate=true&description=false&individual_types=false"
    response = requests.get(nodenorm).json()
    return response[curie]

def in_robokop(nodenorm_id):
    robokop=f"https://automat.renci.org/robokopkg/biolink%3ANamedThing/{nodenorm_id}"
    response = requests.get(robokop).json()
    return len(response) > 0

data = []
with open("drugs_not_in_kg_0_3_6.txt","r") as inf:
    h=inf.readline().strip().split("\t")
    print(h)
    id_col = h.index("id")
    name_col = h.index("drug_name")
    combo_col = h.index("combination_therapy")
    for line in inf:
        x = line[:-1].split("\t")
        data.append( { "id": x[id_col],
                       "name": x[name_col],
                       "combination": x[combo_col] } )

for datum in data:
    nn = get_equivalent(datum["id"])
    if nn is None:
        datum["nodenorm_id"] = None
        continue
    nnid = nn["id"]["identifier"]
    datum["nodenorm_id"] = nnid
    eqids = [x["identifier"] for x in nn["equivalent_identifiers"]]
    prefixes = set( [x.split(":")[0] for x in eqids] )
    datum["has_rxcui"] = "RXCUI" in prefixes

for datum in data:
    datum["in_robokop"]=in_robokop(datum["nodenorm_id"])

df = pd.DataFrame(data)
df.to_csv("drug_check.csv",index=False)