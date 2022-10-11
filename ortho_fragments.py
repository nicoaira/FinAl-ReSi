import re
from Bio import SeqIO
from Bio.Seq import Seq
import sys
import subprocess
import pandas as pd
import time
import argparse
import re
import os
import shutil

parser=argparse.ArgumentParser()

parser.add_argument("-file",
                    help="fasta file with fragments",
                    type=str
                    )

parser.add_argument("-db",
                    help="path to the blast database",
                    type=str
                    )


parser.add_argument("-wordsize",
                    help="blast wordsize parameter",
                    default = '7',
                    type=str
                    )

parser.add_argument("-evalue",
                    help="blast evalue parameter",
                    default = '50',
                    type=str
                    )

parser.add_argument("-blastfmt",
                    help="blast output format",
                    default = '7',
                    type=str
                    )
#
# parser.add_argument("-out",
#                     help="name of output file",
#                     default = None,
#                     type=str
#                     )

args=vars(parser.parse_args())

file = args['file']
db = args['db']
word_size = args['wordsize']
evalue = args['evalue']
outfmt = args['blastfmt']
# outfile = args['out']

c = 1

dir = 'results'

if os.path.exists(dir):
    shutil.rmtree(dir)

os.makedirs(dir)

time.sleep(5)


with open(file) as handle:
    for record in SeqIO.parse(handle, "fasta"):

        seq = record.seq

        print('Fragmento = ', c)

        SeqIO.write(record, "query_fragment.fasta", "fasta")
        print(record)

        os.mkdir(('results/' + 'fragment_' + str(c) + '/'))

        save_path = ('results/' +
                    'fragment_' + str(c) + '/' +
                    'fragment_' + str(c) +
                    '_hits')

        blast_cmd = [
                    'blastn',
                    '-query', 'query_fragment.fasta',
                    '-db', db,
                    '-word_size', word_size,
                    '-evalue',  evalue,
                    '-outfmt', outfmt,
                    '-out', save_path
                    ]

        blastn = subprocess.run(blast_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        os.remove('query_fragment.fasta')

        seq_cmd = [ 'sed',
                    '-i', '1 i\#' + 'seq=' + str(seq),
                    save_path
                    ]

        sequence = subprocess.run(seq_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        c += 1
