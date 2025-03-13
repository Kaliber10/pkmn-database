# pkmn-database

## Syntax

The syntax for most pieces of infomation is self explanitory,
such as name, category, index, and stats.

The syntax for evolutions was designed to be as programmatic as possible.
It would not be a description (ie a string) of how the Pokemon evolved.
The goal is to be laid out as if it was the code in the games,
and was used to determine the evolution.

### Evolutions

It is created as a list of dictionaries to support split evolutions.
There are two key elements of the dictionary,
and they are 'method' and 'pokemon'.

The 'pokemon' element is a dictionary with a string inside which is the name of the pokemon that it is being evolved into. That has an id of 'name'.

The 'method' element can be more complex.

The most simple permutation of evolutions is on level up.
This will look like
    method:
      level : int
Where the int is the level at which the pokemon evolves.

An evolution that relies on friendship will look like
    method:
      happiness:
        eq_exceeds : int
Where the int is the happiness points required for the pokemon to evolve.
Even though the typical happiness evolution is always exceeding 220 in the games,
this allows options for different points of happiness or split evolution depending on happiness.

An evolution that relies on an item will look like
    method:
     item: str
Where the str is the item name that will evolve the pokemon.

An evolution that is a level up but there is another condition will have that condition stated.
    method:
      level: int
      condition:
        time: str
For example, this is a condition where the pokemon evolves at a certain time of day at a certain level.

### Forms

Transformations are when a Pokemon changes form in the middle of battle.
These will have activation and deactivation conditions.
Activation will be what triggers the transformation to the form.
Deactivation will be what triggers the transformation to something different.
If another form is not specified in the activation section,
it is implied to be from any other form.
If another form is not specified in the deactivation section,
it is implied to revert back to its base form.

___Note:___ A Pokemon has a transformation when it can change its shape on its own (depending on the condition).
It has a variation when it has a permanent difference between species.
No current Pokemon in the database has a variation at the moment.
