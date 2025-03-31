import sys
import yaml
import traceback
import pathlib
import shutil
import operator

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
    if not block: # If it is an empty string, do nothing
        return block
    lines = block.split("\n")[:-1] # split on every new line, but remove the extra blank from Python
    reformatted = []
    for line in lines:
        reformatted.append(" " * indent + line) # This will add the indent.
    r = "\n".join(reformatted)
    r += "\n" # Return the newline that was stripped earlier
    return r

def _evo_method_formatter(method: dict):
    if len(method) == 1 and list(method) == ["level"]:
        return f"Level {method['level']}"
    if len(method) == 2 and "level" in method and "condition" in method:
        if list(method["condition"]) == ["gender"]:
            return f"Level {method['level']} while {method['condition']['gender'].title()}"
        if list(method["condition"]) == ["time"]:
            return f"Level {method['level']} during {method['condition']['time'].title()}"
        if list(method["condition"]) == ["hold"]:
            if method["level"] == 1:
                return f"Level Up While Holding {method['condition']['hold'].title()}"
            else:
                return f"Level {method['level']} While Holding {method['condition']['hold'].title()}"
    if len(method) == 1 and list(method) == ["item"]:
        return f"Use {method['item']}"
    if len(method) == 1 and list(method) == ["happiness"]:
        if len(method["happiness"]) == 1 and list(method["happiness"]) == ["eq_exceeds"]:
            return f"Happiness Level Reaches {method['happiness']['eq_exceeds']}"
    return str(method) # This is to make sure some string is always returned.

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
        if "transformations" in data:
            self.transformations = data["transformations"]
        else:
            self.transformations = None
        self.stats = data["stats"]

    def _build_stats_table(self):
        # This is the order to print the stats
        stat_order = ["hp", "attack", "defense", "special attack", "special defense", "speed"]
        table  = "<h2>Stats</h2>\n"
        table += "<div class=\"stat-table\">\n"
        for stat in stat_order:
            css_class = stat.replace(" ", "")
            block  = f"  <div class=\"stat-name-{css_class} stat-cell\">{stat}</div>\n"
            block += f"  <div class=\"stat-value-{css_class} stat-cell\">{self.stats[stat]}</div>\n"
            block += f"  <div class=\"stat-bar-{css_class} stat-cell\">\n"
            block += f"    <svg height=\"100%\" width=\"100%\">\n"
            block += f"      <rect fill=\"black\" width=\"{self.stats[stat]}px\" height=\"100%\" />\n"
            block += f"    </svg>\n"
            block += f"  </div>\n"
            table += block
        table += "</div>\n"

        return table

    def _build_nav_bar(self):
        block = "<nav>\n"
        if self.neighbors[0]:
            block += f"  <a href=\"{self.neighbors[0][0]}.html\">{self.neighbors[0][1]}</a>\n"
        block += "  <a href=\"/index.html\">Home</a>\n"
        if self.neighbors[1]:
            block += f"  <a href=\"{self.neighbors[1][0]}.html\">{self.neighbors[1][1]}</a>\n"
        block += "</nav>\n"

        return block

    def _build_evolution_table(self):

        block = "<h2>Evolutions</h2>\n"
        if not self.evolutions:
            block += "<p>There are no evolutions</p>\n"
        else:
            metadata = self.evolutions.pop() # Pop off the metadata to be used.
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
                # pre-evolution : evolution, next evolutions, method, evolution index
                tree[row[0]].append((row[1], tree[row[1]], row[2], metadata[row[1]]))

            block +=  "<div class=\"evo-item\">\n"
            block +=  "  <ul class=\"evo-row\">\n"
            block += f"    <li class=\"evo-element\">{base}</li>\n"
            block +=  "  </ul>\n"
            for a in sorted(tree[base], key=operator.itemgetter(3)):
                block +=  "  <div class=\"evo-item\">\n"
                block +=  "    <ul class=\"evo-row\">\n"
                block += f"      <li class=\"evo-element\">{_evo_method_formatter(a[2])}</li>\n"
                block +=  "      <li class=\"evo-arrow\">&rarr;</li>\n"
                block += f"      <li class=\"evo-element\">{a[0]}</li>\n"
                block +=  "    </ul>\n"
                for b in sorted(a[1], key=operator.itemgetter(3)):
                    block +=  "    <div class=\"evo-item\">\n"
                    block +=  "      <ul class=\"evo-row\">\n"
                    block += f"        <li class=\"evo-element\">{_evo_method_formatter(b[2])}</li>\n"
                    block +=  "        <li class=\"evo-arrow\">&rarr;</li>\n"
                    block += f"        <li class=\"evo-element\">{b[0]}</li>\n"
                    block +=  "      </ul>\n"
                    block +=  "    </div>\n"
                block +=  "  </div>\n"
            block +=  "</div>\n"

        return block

    def _build_transformations(self):
        if not self.transformations:
            block = ""
        else:
            block  = "<h2>Form Changes</h2>\n"
            for t in self.transformations:
                block  += f"<h3>{t['name']} Form</h3>\n"
                # Put how the form changes here
                # Block += "<p> </p>\n"
                block += f"<ul class=\"type-list\">\n"
                for ft in t["types"]:
                    block += f"  <li class=\"type-icon-{ft.lower()}\">{ft}</li>\n"
                block +=  "</ul>\n"
                condition_text = ""
                if "holding" in t["condition"]["activation"]:
                    if "inclusion" in t["condition"]["activation"]["holding"]:
                        condition_text += f"Changes into {t['name']} while holding " + ", ".join(t["condition"]["activation"]["holding"]["inclusion"]) + "<br>"
                if "holding" in t["condition"]["deactivation"]:
                    if "exclusion" in t["condition"]["deactivation"]["holding"]:
                        condition_text += f"Reverts into Base form when not holding " + ", ".join(t["condition"]["deactivation"]["holding"]["exclusion"])

                block += f"<p>{condition_text}</p>\n"
                block += f"<h4>Stats</h4>\n"
                block +=  "<div class=\"stat-table\">\n"
                for stat in ["hp", "attack", "defense", "special attack", "special defense", "speed"]:
                    css_class = stat.replace(" ", "")
                    block += f"  <div class=\"stat-name-{css_class} stat-cell\">{stat}</div>\n"
                    block += f"  <div class=\"stat-value-{css_class} stat-cell\">{t['stats'][stat]}</div>\n"
                    block += f"  <div class=\"stat-bar-{css_class} stat-cell\">\n"
                    block += f"    <svg width=\"100%\" height=\"100%\">\n"
                    block += f"      <rect width=\"{t['stats'][stat]}px\" height=\"100%\" fill=\"black\" />\n"
                    block += f"    </svg>\n"
                    block += f"  </div>\n"
                block += "</div>\n"

        return block

    def build_page(self):
        page  =  "<!DOCTYPE html>\n"
        page +=  "<html>\n"
        page +=  "  <head>\n"
        page +=  "    <link rel=\"stylesheet\" href=\"/styles/styles.css\" />\n"
        page +=  "  </head>\n"
        page +=  "  <body>\n"
        page += _html_block_indenter(self._build_nav_bar(), 4)
        page += f"    <h1>{self.name}</h1>\n"
        page +=  "    <ul class=\"type-list\">\n"
        for t in self.types:
            page += f"      <li class=\"type-icon-{t.lower()}\">{t}</li>\n"
        page +=  "    </ul>\n"
        page += _html_block_indenter(self._build_stats_table(), 4)
        page += _html_block_indenter(self._build_transformations(), 4)
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

    index_tracker = {} # Create a list of pokemon by index number
    index_map = {} # Create a map of Pokemon names to their index number
    evolution_table = [] # Create a table of all evolutions formatted where each row is "Pre-evolution, Evolution, Method"
    evolution_tracker = {} # Create a map of Pokemon to a list that contains all indexes that reference them in the evolution_table
    # Get the data to make it easier to build the files
    for entry in pokemon:
        data = yaml.safe_load(open(entry.path, "r"))
        # The index table is used for linking to pages, so the name used for the file is used.
        index_tracker[data['index']] = (entry.name, data["name"],)
        index_map[data['name']] = data['index']
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

    site_loc = pathlib.Path(top).joinpath("site")
    if not site_loc.exists():
        site_loc.mkdir()
    styles_dir = site_loc.joinpath("styles")
    if not styles_dir.exists():
        styles.dir.mkdir()
    shutil.copy(top.joinpath("page_resources/site-style.css"), styles_dir.joinpath("styles.css"))
    pokemon_pages = site_loc.joinpath("pokemon")
    if not pokemon_pages.exists():
        pokemon_pages.mkdir()
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
                poke_stack = [] # This stack will collect Pokemon found in each row, to be examined later
                poke_visited = set() # Track what Pokemon we've examined to avoid repeats
                visited = set() # Track what rows in the evolution table we've looked at to avoid redundant examinations
                family = [] # The list of rows from the evolution table that involve the respective Pokemon line
                # Start with the Pokemon currently being read
                # Look through each row in the evolution table that references the Pokemon
                # Evolution Tracker => Pokemon : [row_index, row_index...]
                # Evolution Table => [Pre-evolution, Evolution, Method] (this is a row)
                for i in evolution_tracker[data["name"]]:
                    visited.add(i) # Immediately add the Pokemon to the visited set
                    row = evolution_table[i]
                    family.append(row)
                    if row[0] == data["name"]: # was the pokemon the prevolution
                        poke_stack.append(row[1])
                    else:
                        poke_stack.append(row[0])
                poke_visited.add(data["name"]) # After processing, add the Pokemon to the set
                # Loop until every Pokemon in the line has been examined
                while len(poke_stack) > 0:
                    target = poke_stack.pop()
                    # Do the same thing that was done above
                    for i in evolution_tracker[target]:
                        if i in visited:
                            continue # We already recorded this
                        visited.add(i)
                        row = evolution_table[i]
                        family.append(row)
                        if row[0] == target and row[1] not in poke_visited: # Do not add a Pokemon that was already examined
                            poke_stack.append(row[1])
                        elif row[0] not in poke_visited:
                            poke_stack.append(row[0])
                    poke_visited.add(target)
                # To help with ordering split evolutions, the index of each Pokemon in the line is gathered, and passed to the family object
                meta_index = {name: index_map[name] for name in poke_visited}
                # Put the metadata information at the end so that it can be popped off in the future
                family.append(meta_index) # Include the metadata about the index numbers per Pokemon

            builder = PokemonBuilder(data, neighbors, family)
            with open(pathlib.Path(pokemon_pages).joinpath(entry.name + ".html"), "w+") as f:
                f.write(builder.build_page())
        except:
            traceback.print_exc()
            return 1

    index_page = _build_index_page(index_tracker)
    with open(site_loc.joinpath("index.html"), "w+") as index:
        index.write(index_page)

    return 0

if __name__ == "__main__":
    sys.exit(main())
