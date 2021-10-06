#starter script to run indexer
#clean and create output directory

# format of aruguments for the script
#./index.sh <path to wiki dump XML folder> <path to inverted index output folder> <path to statistics .txt file>

rm -rf $2
mkdir $2

python3 indexer.py $1 $2 $3


