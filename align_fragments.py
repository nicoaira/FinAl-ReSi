import pandas as pd
from Bio import SeqIO
import os
import re
import sys
import subprocess
import argparse

parser=argparse.ArgumentParser()

parser.add_argument("-hits",
                    help="path to the fragments_hits directories",
                    type=str,
                    default='results/'
                    )

parser.add_argument("-db",
                    help="path to the fasta database",
                    type=str
                    )

# parser.add_argument("-out",
#                     help="name of output file",
#                     default = None,
#                     type=str
#                     )

args=vars(parser.parse_args())

hits_path = args['hits']
db_file = args['db']
# outfile = args['out']


cols = ['query acc.ver', 'subject acc.ver', '% identity', 'alignment length', 'mismatches',
 'gap opens', 'q. start', 'q. end', 's. start', 's. end', 'evalue', 'bit score']

cols_map = {i: cols[i] for i in range(len(cols))}


for directory in os.listdir(hits_path):
    filepath = hits_path + '/' + directory + '/' + directory + '_hits'

    with open(filepath, 'r') as f:

        lineas = f.readlines()
        ref_start = int(re.search('(?<=start=)\d+', lineas[2]).group())
        ref_enz_5_pos = int(re.search('(?<=enz_5_pos=)\d+', lineas[2]).group())
        ref_enz_3_pos = int(re.search('(?<=enz_3_pos=)\d+', lineas[2]).group())
        ref_end = int(re.search('(?<=end=)\d+', lineas[2]).group())
        ref_query_size = int(re.search('(?<=size=)\d+', lineas[2]).group())
        ref_seq = re.search('(?<=seq=)\S+', lineas[0]).group()

    df = pd.read_csv(filepath, comment='#', sep='\t', header = None)
    df.rename(columns = cols_map, inplace = True)
    df = df[df['alignment length'] > ref_query_size*0.5]
    df2 = df.sort_values('evalue', ascending=False).drop_duplicates(['subject acc.ver']) #?


    header = (  '>'+ 'Reference_genome' +
                ' start=' + str(ref_start) +
                ' enz_5_pos=' + str(ref_enz_5_pos) +
                ' enz_3_pos=' + str(ref_enz_3_pos) +
                ' end=' + str(ref_end) + '\n'
                )

    subjects_save_path = (  hits_path + '/' +
                            directory + '/' +
                            directory +'_hits_seqs.fasta')

    with open(subjects_save_path,  'w') as j:
        j.write(header)
        j.write(str(ref_seq))
        j.write('\n')


    with open(db_file) as handle:
        for record in SeqIO.parse(handle, "fasta"):

            seq = record.seq
            genome_name = record.name

            genome_start = df.loc[df['subject acc.ver'] == genome_name, 's. start'].values[0] -1
            genome_end = df.loc[df['subject acc.ver'] == genome_name, 's. end'].values[0]

            header = (  '>'+ genome_name +
                        ' start=' + str(genome_start) +
                        ' end=' + str(genome_end) + '\n'
                        )

            with open(subjects_save_path, 'a') as j:
                j.write(header)
                j.write(str(seq[genome_start:genome_end]))
                j.write('\n')

    alignment_save_path = ( hits_path + '/' +
                            directory + '/' +
                            directory +'_hits.aln')

    muscle_cmd = [
                'muscle',
                '-in', subjects_save_path,
                '-out', alignment_save_path,
                    ]

    muscle = subprocess.run(muscle_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
