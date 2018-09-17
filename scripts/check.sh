#!/bin/bash
filenames=()
while IFS=  read -r -d $'\0'; do
  filenames+=("$REPLY")
done < <(find $1 -name "*_t.c" -print0)

for filename in ${filenames[@]}
do
   [ $filename =~ "\/([a-zA-Z][a-zA-Z0-9]*)_t.c" ]
   functionname="${BASH_REMATCH[1]}"
   echo -e "\033[92mChecking \033[1m$filename\033[0m \033[92mwith \033[31;1mMathSat\033[0m"
   ./cpachecker/scripts/cpa.sh -predicateAnalysis $filename -preprocess -entryfunction functionname
   echo -e "\033[92mChecking \033[1m$filename\033[0m \033[92mwith \033[31;1mSMT-Interpol\033[0m"
   ./cpachecker/scripts/cpa.sh -predicateAnalysis $filename -preprocess -setprop solver.solver=smtinterpol -entryfunction functionname
   echo -e "\033[92mChecking \033[1m$filename\033[0m \033[92mwith \033[31;1mZ3\033[0m"
   ./cpachecker/scripts/cpa.sh -predicateAnalysis $filename -preprocess -setprop solver.solver=z3 -entryfunction functionname
done
