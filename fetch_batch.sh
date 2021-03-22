path=$(pwd)
export PYTHONPATH="$path:$PYTHONPATH"
python3 $path/data_fetcher/fetch.py --type games --batch_size 40
