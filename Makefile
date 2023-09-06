SHELL:=/bin/bash

all:
	@echo "choose explicit target = type 'make ' and press TAB"

S=scripts
I=data
O=out


# ===== MAIN STUFF 

DATASET=freq-exam-no-közösségi-prob-val.txt

process:
	cat $I/$(DATASET) | python3 $S/process.py --all > predataset.csv
	cat $I/$(DATASET) | python3 $S/process.py --dedup > dataset.csv

