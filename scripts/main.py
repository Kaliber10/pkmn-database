import sys
import yaml
import traceback
import pathlib

# This is a list of helper functions
class DBEntry():
    '''A instance of a database entry
    
    This is a representative of an entry that is the name of the file, where the name is the
    true name (not the split name), and the path to the file to access the data.
    '''
    def __init__(self, cat, name, path):
        self.type = cat
        self.name = name
        self.path = path

    def __str__(self):
        return f"{self.name} of db:{self.type}@{self.path}"

def _list_db_files(db: pathlib.Path):
    '''Create a list of database entries from a database path

    This creates a list of all the entries/files in a database path. This makes it easier
    to access.
    '''
    info = []
    for e in db.glob('**/*.yaml'):
        # The name is formed by the two chars of the directory and the rest of the file,
        # except for the exception.
        name = e.parts[-2] + e.parts[-1].split(".")[0]
        info.append(DBEntry(e.parts[-3], name, str(e)))
    return info
# End helper section

def main():
    
    # Set the path to the top of the project so that it is consistent when searching for files.
    main_location = pathlib.Path(__file__)
    top = main_location.parent.parent # This will be the top level of the project

    db_pokemon = pathlib.Path(top).joinpath("db/pokemon") # Add the path to the pokemon database
    pokemon = _list_db_files(db_pokemon) 

    index_tracker = {}
    evolution_table = []
    evolution_tracker = {}
    # Get the data to make it easier to build the files
    for entry in pokemon:
        data = yaml.safe_load(open(entry.path, "r"))
        index_tracker[data['index']] = data["name"]
        if "evolutions" in data:
            for evo in data["evolutions"]:
                evolution_table.append((data["name"], evo["pokemon"]["name"], evo["method"],))
                if data["name"] in evolution_tracker:
                    # Since it is tracking the latest evolution added
                    evolution_tracker[data["name"]].append(len(evolution_table) - 1)
                else:
                    evolution_tracker[data["name"]] = [len(evolution_table) - 1]
    # This will convert the dictionary to a list
    index_tracker = [x[1] for x in sorted(index_tracker.items(), key=lambda x: x[0])]
    # Now all the hard to grab data is collected.

if __name__ == "__main__":
    sys.exit(main())
