from driftlon_utils import get_connection_for_collection_name

def main():
    db, matches_collection = get_connection_for_collection_name('matches')
    matches = matches_collection.find()
    print(len(matches))


if __name__ == '__main__':
    main()
