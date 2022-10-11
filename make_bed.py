import re
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Restriction import *
from collections import Counter
import collections
import argparse
import re
import pandas as pd


parser=argparse.ArgumentParser()


parser.add_argument("-file",
                    help="fasta file with the fragments",
                    type=str
                    )

parser.add_argument("-name",
                    help="the name of the chromosome or scaffold",
                    type=str
                    )

parser.add_argument("-desc",
                    help="description of the track",
                    default = 'Restriction fragments found',
                    type=str
                    )

parser.add_argument("-track",
                    help="name of the track",
                    default = 'Restriction fragments',
                     type=str
                     )

# parser.add_argument("-out",
#                     help="name of output file",
#                     default = 'fragments.bed',
#                     type=str
#                     )

args=vars(parser.parse_args())

file = args['file']
name = args['name']
desc = args['desc']
track = args['track']
# outfile = args['out']

enzimes_combinations = {}
dict_df = {'chr' : name , 'start' : [], 'end' : []}


with open(file) as handle:
    for record in SeqIO.parse(handle, "fasta"):

        seq = record.seq
        header = record.description

        sites = re.search('(?<=sites=)\S+', header).group()
        start = re.search('(?<=start=)\d+', header).group()
        end = re.search('(?<=end=)\d+', header).group()

        if sites not in enzimes_combinations:
            enzimes_combinations[sites] = { 'chr' : name ,
                                            'start' : [],
                                            'end' : []
                                            }

        enzimes_combinations[sites]['start'].append(start)
        enzimes_combinations[sites]['end'].append(end)

for k, v in enzimes_combinations.items():
    print(k)
    bed_df = pd.DataFrame(v)
    print(bed_df)

    outfile = 'fragments_' + k + '.bed'

    head = ('track name=' + track + '\t'
            'description="' + desc + '"' + '\n')

    with open(outfile, 'w') as f:
        f.write(head)

    bed_df.to_csv(outfile, sep='\t', header=None, index = False, mode = 'a')
