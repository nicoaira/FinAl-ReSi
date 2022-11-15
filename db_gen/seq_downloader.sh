#!/bin/bash

cd ..
mkdir rep_genomes

git clone https://github.com/enasequence/enaBrowserTools.git

while read p; do
  enaBrowserTools/python3/enaDataGet $p -f fasta -d rep_genomes
done < embl-idlist.txt

cd rep_genomes

rmdir *

cat *.fasta > sars_db.fasta

makeblastdb -in REP-SARS-DB.fasta -dbtype nucl -out sars_db -title "SARS_db"
