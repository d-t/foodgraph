from collections import Counter
import csv
import json
import math
import sys

import networkx as nx


# TODO: top-n connections (n as paramter)

# ----- I/O Functions ----- #

def _load_recipes_json(filepath):
    """
    Load input file containing recipes and ingredients as json.
    """
    with open(filepath, 'rb') as f:
        json_recipes = json.load(f)
    return json_recipes


def _write_to_file(x, output_filepath):
    """
    Write input object to a csv file.
    """
    with open(output_filepath, 'wb+') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(x)


# ----- Ingredients Functions ----- #

def _get_ing_name2id_dict(json_recipes):
    """
    Create a dict object converting ingredient name to id.
    """
    ing_name2id = {}  # output variable
    ing_id_counter = 0  # id
    for recipe in json_recipes:
        for ing_name in recipe['ingredients']:
            ing_name = ing_name.encode('utf8')
            if ing_name not in ing_name2id:
                ing_name2id[ing_name] = ing_id_counter
                ing_id_counter += 1
    return ing_name2id


def _count_ingredients(json_recipes, ing_name2id):
    """
    Count the number of recipes each ingredient is associated with.
    Return a Counter object with recipe frequency for each ingredient id.
    """
    ing_cnt = Counter()  # output variable
    for recipe in json_recipes:
        for ing_name in recipe['ingredients']:
            ing_name = ing_name.encode('utf8')
            if ing_name in ing_name2id:  # if name exists...
                ing_id = ing_name2id[ing_name]
                ing_cnt[ing_id] += 1
    return ing_cnt


def _ing_id2name(ing_id, ing_name2id):
    """
    Given an ingredient id as input, search for corresponding name.
    """
    try:
        ing_name = [x for x in ing_name2id if ing_name2id[x]==ing_id][0]
    except Exception, e:
        print e
        ing_name = ''
    return ing_name


# -----  Ingredients + Recipes Functions ----- #

def _get_recipe2ingredients_dict(json_recipes, ing_name2id):
    recipe2ings = {}
    for recipe in json_recipes:
        if recipe['id'] not in recipe2ings:
            recipe2ings[recipe['id']] = []
        for ing_name in recipe['ingredients']:
            ing_name = ing_name.encode('utf8')
            if ing_name in ing_name2id:
                ing_id = ing_name2id[ing_name]
                recipe2ings[recipe['id']].append(ing_id)
    return recipe2ings


def _get_ing2recipes_dict(json_recipes, ing_name2id):
    ing2recipes = {}
    for recipe in json_recipes:
        for ing_name in recipe['ingredients']:
            ing_name = ing_name.encode('utf8')
            ing_id = ing_name2id[ing_name]
            if ing_id not in ing2recipes:
                ing2recipes[ing_id] = []
            ing2recipes[ing_id].append(recipe['id'])
    return ing2recipes


def _get_ing2ingredients_dict(ing2recipes, recipe2ings, ing_cnt):
    """
    Create the dict object associating each ingredient to other ingredients with recipes
    in common.

    Args:
        ing2recipes: dict associating ingredient ids to recipes
        recipe2ings: dict associating recipe ids to ingredients
        ing_cnt: Counter object containing the number of recipes each ingredient is
                 associated with

    Returns:
        ing2ingredients: dict object associating ingredient ids to each other
    """
    ing2ingredients = {}  # output variable
    n_recipes = len(recipe2ings)

    for ing_id_1 in ing2recipes:  # for each primary ingredient...
        if ing_id_1 not in ing2ingredients:
            ing2ingredients[ing_id_1] = {}
        for recipe_id in ing2recipes[ing_id_1]:
            recipe_ingredients = recipe2ings[recipe_id]
            for ing_id_2 in recipe_ingredients:
                if ing_id_2 != ing_id_1:
                    if ing_id_2 not in ing2ingredients[ing_id_1]:
                        ing2ingredients[ing_id_1][ing_id_2] = 0
                    ing2ingredients[ing_id_1][ing_id_2] += 1

        for ing_id_2 in ing2ingredients[ing_id_1]:  # ...for each secondary ingredient...
            # ...calculate term-frequency and inverse-document-frequency for edge weight
            tf = ing2ingredients[ing_id_1][ing_id_2]
            idf = math.log(n_recipes / ing_cnt[ing_id_2])
            ing2ingredients[ing_id_1][ing_id_2] = tf * idf

    return ing2ingredients


# ----- Graph Functions ----- #

def create_graph(ing2ingredients, ing_name2id, ing_cnt):
    """
    Create a graph object for ingredients.
    Each node is an ingredient, characterized by id, name and number of recipes.
    Each edge is an undirected connection between ingredients contained in same recipes.
    The edge weight is calculated using tf-idf.

    Args:
        ing2ingredients: dict object associating ingredient ids to each other
        ing_cnt: Counter object containing the number of recipes each ingredient is
                 associated with

    Returns:
        g: networkx graph of ingredients
    """
    g = nx.Graph()  # output variable

    # Add each ingredient as node
    for ing_id_1 in ing2ingredients:
        g.add_node(ing_id_1, name=_ing_id2name(ing_id_1, ing_name2id),
                   n_recipes=ing_cnt[ing_id_1])
        # Add related ingredients as edges
        for ing_id_2 in ing2ingredients[ing_id_1]:
            g.add_edge(ing_id_1, ing_id_2, weight=ing2ingredients[ing_id_1][ing_id_2])

    # Return graph
    return g


def get_nodes_list(g):
    """
    Extract list of nodes from graph object.
    """
    # Define output variable and add header strings
    nodes_list = [['Id', 'Label', 'N Recipes']]

    # Loop through graph nodes
    for ing_id in g.nodes():
        row = [ing_id]
        ing_data = g.node[ing_id]
        row.append(ing_data['name'])
        row.append(ing_data['n_recipes'])
        nodes_list.append(row)

    # Return nodes' list
    return nodes_list


def get_edges_list(g):
    """
    Extract list of edges from graph object.
    """
    # Extract list of edges
    edges_list = [['Source', 'Target', 'Weight']]

    # Loop through graph edges
    for ings_pair in g.edges():
        row = [ings_pair[0], ings_pair[1]]
        row.append(g[ings_pair[0]][ings_pair[1]]['weight'])
        edges_list.append(row)

    # Return edges' list
    return edges_list


# ----- Main Function ----- #

def main(args):
    """
    Main function, performing the following operations:
      - load input data
      - extract ingredients' support objects and information, e.g. number of associated
        recipes and id-to-name conversion object
      - extract recipes' support objects, e.g. recipe-to-ingredient object
      - create ingredients' graph
      - write nodes' and edges' list to file

    Args:
        args: list of input arguments, i.e.
                - filepath: string, path to input file
                - nodes_output_filepath: string, path to output nodes file to be written
                - edges_output_filepath: string, path to output edges file to be written

    Returns:
        g: networkx graph of ingredients
    """
    # Constants
    INPUT_FILEPATH = '../dataset/kaggle_recipes.json'
    DEFAULT_OUTPUT_FILEPATH_NODES = '../output/nodes.csv'
    DEFAULT_OUTPUT_FILEPATH_EDGES = '../output/edges.csv'

    # Input file path
    if len(args) == 0:
        filepath = INPUT_FILEPATH
    else:
        filepath = args[0]

    # Load recipes
    print "Load input file"
    try:
        json_recipes = _load_recipes_json(filepath)
    except Exception, e:
        print e

    # Get support objects
    print "Process ingredients"
    ing_name2id = _get_ing_name2id_dict(json_recipes)
    ing_cnt = _count_ingredients(json_recipes, ing_name2id)
    print "Process recipes"
    recipe2ings = _get_recipe2ingredients_dict(json_recipes, ing_name2id)
    ing2recipes = _get_ing2recipes_dict(json_recipes, ing_name2id)

    # Create graph
    print "Create graph"
    ing2ingredients = _get_ing2ingredients_dict(ing2recipes, recipe2ings, ing_cnt)
    g = create_graph(ing2ingredients, ing_name2id, ing_cnt)

    # Extract nodes and edges
    nodes_list = get_nodes_list(g)
    edges_list = get_edges_list(g)

    # Write nodes and edges as CSV files
    print "Write nodes and edges to file"
    if len(args) > 1:
        try:
            nodes_output_filepath = args[1]
            edges_output_filepath = args[2]
        except Exception, e:
            print "Error with additional arguments"
            nodes_output_filepath = DEFAULT_OUTPUT_FILEPATH_NODES
            edges_output_filepath = DEFAULT_OUTPUT_FILEPATH_EDGES
    else:
        nodes_output_filepath = DEFAULT_OUTPUT_FILEPATH_NODES
        edges_output_filepath = DEFAULT_OUTPUT_FILEPATH_EDGES
    _write_to_file(nodes_list, nodes_output_filepath)
    _write_to_file(edges_list, edges_output_filepath)

    # Return graph
    return g


if __name__ == '__main__':
    g = main(sys.argv[1:])
