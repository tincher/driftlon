path="/home/tincher"
export PYTHONPATH="$path/projects/driftlon:$PYTHONPATH"
python3 $path/projects/driftlon/data_fetcher/fetch.py --type games --batch_size 40
