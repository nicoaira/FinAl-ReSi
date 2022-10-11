import re
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Restriction import *
from collections import Counter
import collections
import argparse
import re

parser=argparse.ArgumentParser()

parser.add_argument("-file",
                    help="fasta file with reference sequence (genome/gene/region)",
                    type=str
                    )

parser.add_argument("-left",
                    help="add extra bases to the left of found fragment",
                    default = 0,
                     type=int
                     )

parser.add_argument("-right",
                    help="add extra bases to the right of found fragment",
                    default = 0,
                    type=int
                    )

parser.add_argument("-mindist",
                    help="maximum distance between the restriction sites",
                    default = str(10),
                    type=str
                    )

parser.add_argument("-maxdist",
                    help="maximum distance between the restriction sites",
                    default = str(250),
                    type=str
                    )

parser.add_argument("-out",
                    help="name of output file",
                    default = None,
                    type=str
                    )



args=vars(parser.parse_args())

file = args['file']
left = args['left']
right = args['right']
max_distance = args['maxdist']
min_distance = args['mindist']
outfile = args['out']

if outfile != None:
    with open(outfile, 'w') as f:
        pass


bases_dict=   {
                    'A' : '[A]',
                    'T' : '[T]',
                    'C' : '[C]',
                    'G' : '[G]',
                    'R' : '[AG]',
                    'Y' : '[CT]',
                    'M' : '[AC]',
                    'K' : '[GT]',
                    'S' : '[CG]',
                    'W' : '[AT]',
                    'H' : '[ACT]',
                    'B' : '[CGT]',
                    'V' : '[ACG]',
                    'D' : '[AGT]',
                    'N' : '[ACGT]',
                    }

def degenerated_to_regex(site):

    regex_string = []

    c = 1

    for base_pos in range(len(site)):

        if base_pos != len(site) - 1:

            if site[base_pos] == site[base_pos+1]:
                c += 1
                continue

            else:
                base_expresion = bases_dict[site[base_pos]] + '{' + str(c) + '}'
                regex_string.append(base_expresion)
                c = 1
        else:
            base_expresion = bases_dict[site[base_pos]] + '{' + str(c) + '}'
            regex_string.append(base_expresion)


    return ''.join(regex_string)

# Se detalla la secuencia sobre la hebra cortada y
# posicion desde el 5'.
# Ej: NtBstNBI se conrta entre las posiciones 9 y 10

nicking_enzimes = {
                    'Nt.BstNBI': {'site':'GAGTCNNNNN', 'nick_pos' : 9},
                    'Nb.BsrDI': {'site':'NNCATTGC', 'nick_pos' : 2}
                    }


enz_3 = BstNI


with open(file) as handle:
    for record in SeqIO.parse(handle, "fasta"):

        seq = record.seq
        org = record.name
        seq_string = str(seq)

        sites_3 = enz_3.search(seq)

        # sumar dos para contemplar el final del sitio de restriccion
        sites_3 =  [n +2 for n in sites_3]


        for k, v in nicking_enzimes.items():

            site_5 = 0

            regex_site = degenerated_to_regex(v['site'])
            expresion = (regex_site +
                        '.{' + min_distance + ','
                        + max_distance + '}$')

            for site_3 in sites_3:

                match = re.search(expresion, seq_string[site_5:site_3])
                if match != None:
                    fragment_span = re.search(expresion, seq_string[site_5:site_3]).span()
                    enz_5_pos = site_5 + fragment_span[0]

                    if enz_5_pos > left:
                        start = enz_5_pos - left
                    else:
                        start = 0

                    #prevent out of index if working in 3' of genome
                    if site_3 + right < len(seq_string) :
                        end = site_3 + right
                    else:
                        end = len(seq_string) - 1

                    fasta_header = ('>' + org +
                                    ' ; sites=' + k +'-'+ str(enz_3) +
                                    ' ; start='+ str(start + 1) +
                                    ' ; enz_3_pos='+ str(site_3) +
                                    ' ; enz_5_pos='+ str(start) +
                                    ' ; end='+ str(end+1) +
                                    ' ; size='+  str(end-start))

                    fragment_sequence = seq_string[start:end]

                    if outfile == None:
                        print(fasta_header)
                        print(fragment_sequence)

                    else:
                        with open(outfile, 'a') as f:
                            f.write(fasta_header + '\n')
                            f.write(fragment_sequence + '\n')

                site_5 = site_3
