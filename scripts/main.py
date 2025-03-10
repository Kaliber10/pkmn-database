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

def _html_block_indenter(block: str, indent: int):
    '''Helper function to indent a block of HTML for cleaniness'''
    lines = block.split("\n")[:-1] # split on every new line, but remove the extra blank from Python
    reformatted = []
    for line in lines:
        reformatted.append(" " * indent + line) # This will add the indent.
    r = "\n".join(reformatted)
    r += "\n" # Return the newline that was stripped earlier
    return r

class PokemonBuilder():
    '''A instance of Pokemon data that is used to build an HTML page

    This class is supposed to hold the data for a Pokemon and have the functions to output it to HTML.
    '''
    def __init__(self, data, indices, family):
        # The data is the data for the Pokemon
        # The indices are the surrounding indices of the pokemon
        # previous is a tuple of the evolution information for what it evolved from
        self.name = data["name"]
        self.category = data["category"]
        self.index = data["index"]
        self.types = data["types"]
        self.neighbors = indices
        self.evolutions = family
        self.stats = data["stats"]

    def _build_stats_table(self):
        # This is the order to print the stats
        stat_order = ["hp", "attack", "defense", "special attack", "special defense", "speed"]
        table = "<h2>Stats</h2>\n<table>\n"
        for stat in stat_order:
            block =   "<tr>\n"
            block += f"  <th scope=\"row\">{stat}</th>\n"
            block += f"  <td>{self.stats[stat]}</td>" + "\n"
            block +=  "  <td style=\"width:255px\">\n"
            block += f"    <div style=\"background-color:black;height:20px;width:calc(100%*{self.stats[stat]}/255)\"></div>\n"
            block +=  "  </td>\n"
            block +=  "</tr>\n"
            table += _html_block_indenter(block, 2)
        table += "</table>\n"

        return table

    def _build_nav_bar(self):
        block = "<nav>\n"
        if self.neighbors[0]:
            block += f"  <a href=\"{self.neighbors[0][0]}.html\">{self.neighbors[0][1]}</a>\n"
        block += "  <a href=\"../../index.html\">Home</a>\n"
        if self.neighbors[1]:
            block += f"  <a href=\"{self.neighbors[1][0]}.html\">{self.neighbors[1][1]}</a>\n"
        block += "</nav>\n"

        return block

    def _build_evolution_table(self):

        block = "<h2>Evolutions</h2>\n"
        if not self.evolutions:
            block += "<p>There are no evolutions</p>\n"
        else:
            pres = set(x[0] for x in self.evolutions)
            posts = set(x[1] for x in self.evolutions)
            base = pres.difference(posts).pop() # There will only be the base pokemon left
            finals = list(posts - pres) # A potential list of all final evolutions (split evolutions)
            middle = list(pres | posts) # The common elements are the middle evolutions

            # build a list of lists to represent the tree?
            tree = {}
            for k in [base] + middle + finals:
                tree[k] = []

            for row in self.evolutions:
                tree[row[0]].append((row[1], tree[row[1]], row[2],))

            block +=  "<ul>\n"
            block += f"  <li>{base}\n"
            block += f"    <ul>\n"
            for a in tree[base]:
                block += f"      <li>{a[0]}"
                if a[1]:
                    block += "\n        <ul>\n"
                    for b in a[1]:
                        block += f"          <li>{b[0]}</li>\n"
                    block += "        </ul>\n      "
                block += "</li>\n"
            block += f"    </ul>\n"
            block += f"  </li>\n"
            block += f"</ul>\n"

        return block

    def build_page(self):
        page  =  "<!DOCTYPE html>\n"
        page +=  "<html>\n"
        page +=  "  <head>\n"
        page +=  "  </head>\n"
        page +=  "  <body>\n"
        page += _html_block_indenter(self._build_nav_bar(), 4)
        page += f"    <h1>{self.name}</h1>\n"
        page +=  "    <ul style=\"list-style:none\">\n"
        for t in self.types:
            page += f"      <li>{t}</li>\n"
        page +=  "    </ul>\n"
        page += _html_block_indenter(self._build_stats_table(), 4)
        page += _html_block_indenter(self._build_evolution_table(), 4)
        page +=  "  </body>\n"
        page +=  "</html>"

        return page

def _build_index_page(index):
    page  = "<!DOCTYPE html>\n"
    page += "<html>\n"
    page += "  <head>\n"
    page += "  </head>\n"
    page += "  <body>\n"
    page += "    <h1>Database</h1>\n"
    page += "    <div>\n"
    page += "      <h2>Pokemon</h2>\n"
    page += "      <table>\n"
    page += "        <tr>\n"
    page += "          <th>No.</th>\n"
    page += "          <th>Name</th>\n"
    page += "        </tr>\n"
    for i, data in enumerate(index):
        block  =  "        <tr>\n"
        block += f"          <td>{i + 1}</td>\n"
        block +=  "          <td>\n"
        block += f"            <a href=\"pokemon/{data[0]}.html\">{data[1]}</a>\n"
        block +=  "          </td>\n"
        block +=  "        </tr>\n"
        page += block
    page += "      </table>\n"
    page += "    </div>\n"
    page += "  </body>\n"
    page += "</html>"

    return page

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
        # The index table is used for linking to pages, so the name used for the file is used.
        index_tracker[data['index']] = (entry.name, data["name"],)
        if "evolutions" in data:
            for evo in data["evolutions"]:
                evolution_table.append((data["name"], evo["pokemon"]["name"], evo["method"],))
                if data["name"] in evolution_tracker:
                    # Since it is tracking the latest evolution added
                    evolution_tracker[data["name"]].append(len(evolution_table) - 1)
                else:
                    evolution_tracker[data["name"]] = [len(evolution_table) - 1]
                if evo["pokemon"]["name"] in evolution_tracker:
                    evolution_tracker[evo["pokemon"]["name"]].append(len(evolution_table) - 1)
                else:
                    evolution_tracker[evo["pokemon"]["name"]] = [len(evolution_table) - 1]
    # This will convert the dictionary to a list
    index_tracker = [x[1] for x in sorted(index_tracker.items(), key=lambda x: x[0])]
    # Now all the hard to grab data is collected.

    pokemon_pages = pathlib.Path(top).joinpath("pokemon")
    for entry in pokemon:
        try:
            data = yaml.safe_load(open(entry.path, "r"))
            # Because index is 1 indexed, to map it to a list, 1 is considered the first value.
            # The Pokemon's index is actual one value above what their index is in index_tracker.
            if data["index"] == 1:
                neighbors = (None, index_tracker[data["index"]],)
            elif data["index"] == len(index_tracker):
                neighbors = (index_tracker[data["index"] - 2], None,)
            else:
                neighbors = (index_tracker[data["index"] - 2], index_tracker[data["index"]],)
            # family is the table for the evolution line
            if data["name"] not in evolution_tracker:
                family = None
            else:
                poke_stack = []
                poke_visited = set()
                visited = set()
                family = []
                for i in evolution_tracker[data["name"]]:
                    visited.add(i)
                    row = evolution_table[i]
                    family.append(row)
                    if row[0] == data["name"]: # was the pokemon the prevolution
                        poke_stack.append(row[1])
                    else:
                        poke_stack.append(row[0])
                poke_visited.add(data["name"])
                while len(poke_stack) > 0:
                    target = poke_stack.pop()
                    for i in evolution_tracker[target]:
                        if i in visited:
                            continue # We already recorded this
                        visited.add(i)
                        row = evolution_table[i]
                        family.append(row)
                        if row[0] == target and row[1] not in poke_visited:
                            poke_stack.append(row[1])
                        elif row[0] not in poke_visited:
                            poke_stack.append(row[1])
                    poke_visited.add(target)

            builder = PokemonBuilder(data, neighbors, family)
            with open(pathlib.Path(pokemon_pages).joinpath(entry.name + ".html"), "w+") as f:
                f.write(builder.build_page())
        except:
            traceback.print_exc()
            return 1

    index_page = _build_index_page(index_tracker)
    with open(pathlib.Path(top).joinpath("index.html"), "w+") as index:
        index.write(index_page)

    return 0

if __name__ == "__main__":
    sys.exit(main())
