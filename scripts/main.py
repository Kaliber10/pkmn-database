import sys
import yaml
import build_pokemon
import traceback
import pathlib
import pydom

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
        name = e.parts[-2] + e.parts[-1].split(".")[0]
        info.append(DB_Entry(e.parts[-3], name, str(e)))
    return info

def main():
    main_location = pathlib.Path(__file__)
    top = main_location.parent.parent
    pokemon_db = pathlib.Path(top).joinpath("db/pokemon")
    pokemon = _list_db_files(pokemon_db)
    pokemon_pages = pathlib.Path(top).joinpath("pokemon")
    pokemon_pages.mkdir(exist_ok=True)
    index_table = []
    for p in pokemon:
        try:
            f = open(pathlib.Path(pokemon_pages).joinpath(p.name + ".html"), "w+")
            data = yaml.safe_load(open(p.path, "r"))
            build_pokemon.builder(data, f)
            row = pydom.TableRow()
            row.children.append(pydom.TableDataCell())
            row.children.append(pydom.TableDataCell())
            row.children[0].text_content = str(data["index"])
            row.children[1].children.append(pydom.Anchor(href=f"pokemon/{p.name}.html"))
            row.children[1].children[0].text_content = data["name"]
            index_table.append(row)
        except:
            traceback.print_exc()
            return 1

    index_table = sorted(index_table, key=lambda x: x.children[0].text_content)
    dom = pydom.DOM()
    body = dom.top.children[1]
    body.children.append(pydom.Heading1())
    body.children.append(pydom.Div())
    body.children[1].children.append(pydom.Heading2())
    body.children[1].children.append(pydom.Table())
    body.children[0].text_content = "Database"
    body.children[1].children[0].text_content = "Pokemon"
    t = body.children[1].children[1]
    t.children.append(pydom.TableRow())
    t.children[0].children.append(pydom.TableHeader())
    t.children[0].children.append(pydom.TableHeader())
    t.children[0].children[0].text_content = "No."
    t.children[0].children[1].text_content = "Name"
    for e in index_table:
        t.children.append(e)
    index_page = open(pathlib.Path(top).joinpath("index.html"), "w+")
    dom.print(stream=index_page)
    return 0

if __name__ == "__main__":
    sys.exit(main())