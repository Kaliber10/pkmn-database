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

def _list_db_files(dir: str):
    p = pathlib.Path(dir)
    info = []
    for e in p.glob('*.yaml'):
        name = e.parts[0] + e.parts[1]
        info.append(DB_Entry(dir, name, str(e)))
    return info    

def main():
    current = __file__
    pokemon = _list_db_files(current + '../db/pokemon')

    for p in pokemon:
        data = yaml.safe_load(current + "../db/pokemon/" + p.path)
        try:
            build_pokemon.builder(data)
        except:
            traceback.print_exc()
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())