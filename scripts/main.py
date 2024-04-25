import sys
import yaml
import build_pokemon
import traceback
import pathlib

class DB_Entry():

    def __init__(self, type, name, path):
        self.type = type
        self.name = name
        self.path = path

    def __str__(self):
        return f"{self.name} of db:{self.type}@{self.path}"

def _list_db_files(db: pathlib.Path):

    info = []
    for e in db.glob('**/*.yaml'):
        name = e.parts[-2] + e.parts[-1]
        info.append(DB_Entry(e.parts[-3], name, str(e)))
    return info    

def main():
    main_location = pathlib.Path(__file__)
    top = main_location.parent.parent
    pokemon_db = pathlib.Path(top).joinpath("db/pokemon")
    pokemon = _list_db_files(pokemon_db)

    for p in pokemon:
        try:
            data = yaml.safe_load(open(p.path))
            build_pokemon.builder(data)
        except:
            traceback.print_exc()
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())