import csv
import json
import os
import sys


# ---------- Support Functions ---------- #

def get_recipes_list(recipes_json):
    """
    Process the original json structure and get information for each recipe.

    The returned object is a list, each item containing:
        - recipe id
        - cuisine
        - number of ingredients
    """

    recipes = []  # output variable
    for recipe in recipes_json:
        # Get information
        r_id = recipe['id']
        r_cuisine = recipe['cuisine']
        n_ingredients = len(recipe['ingredients'])
        # Append to final list
        row = [r_id, r_cuisine, n_ingredients]
        recipes.append(row)
    return recipes


def get_ingredients_list(recipes_json):
    """
    Process the original json structure and get information for each ingredient.

    The returned object is a list, each item containing:
        - ingredient id
        - ingredient name
    """

    ingredients = []  # output variable
    ingredients_names = []
    ing_id = 0  # counter
    for recipe in recipes_json:
        r_ingredients = recipe['ingredients']
        for ing in r_ingredients:
            ing = ing.encode('utf8')
            if ing not in ingredients_names:
                row = [ing_id, ing]
                ingredients_names.append(ing)
                ingredients.append(row)
                ing_id += 1  # update counter
    return ingredients


def get_ingredient_recipes(recipes_json, ings_name_id):
    """
    For each ingredient, get recipes containing it.
    """

    ing_recipes = {}  # output variable
    for recipe in recipes_json:  # for each recipe...
        r_id = recipe['id']
        for ing in recipe['ingredients']:  # for each ingredient...
            ing = ing.encode('utf8')
            ing_id = ings_name_id[ing]
            if ing_id not in ing_recipes:
                ing_recipes[ing_id] = []
            ing_recipes[ing_id].append(r_id)  # ...add recipe to ingredient
    return ing_recipes


def get_recipes_ingredients(recipes_json, ings_name_id):
    """
    For each recipe, get associated ingredients.
    """

    rec_ingredients = {}
    for recipe in recipes_json:
        r_id = recipe['id']
        rec_ingredients[r_id] = []
        for ing in recipe['ingredients']:
            ing = ing.encode('utf8')
            rec_ingredients[r_id].append(ings_name_id[ing])
    return rec_ingredients


def get_ing_ingredients(ing_recipes, rec_ingredients):
    """
    For each ingredient, get other ingredients co-existing in recipes.
    """

    ing_ingredients = {}  # output variable
    for ing_id in ing_recipes:  # for each "primary" ingredient...
        if ing_id not in ing_ingredients:
            ing_ingredients[ing_id] = {}
        recipes_ids = ing_recipes[ing_id]  # ...get associated recipes
        for r_id in recipes_ids:  # for each recipe...
            ing_ids = rec_ingredients[r_id]  # ...get "secondary" ingredients
            for i_id in ing_ids:  # for each secondary ingredient...
                if i_id != ing_id:
                    if i_id not in ing_ingredients[ing_id]:
                        ing_ingredients[ing_id][i_id] = 0
                    ing_ingredients[ing_id][i_id] += 1
    return ing_ingredients


# ---------- Main Function ---------- #

def write_ingredients_network(args):
    """
    Write ingredients network to file.

    Args:
        - args: list of strings representing filepaths to the input file to be loaded and
                to the output files to be written. In particular:
                  - args[0] is the path to the input dataset file
                  - args[1] is the path to the output ingredient network
                  - args[2] is the path to the output ingredient names

    The input file path is required by the function. If the output file paths are not 
    provided, default ones will be used.
    """

    n_args = len(args)

    # Load dataset
    print "Loading dataset"
    if n_args > 0:
        dataset_path = args[0]
        if dataset_path is not None:
            with open(dataset_path, 'rb') as f:
                recipes_json = json.load(f)

    # Get recipes list, sorted by id
    print "Processing recipes"
    recipes_list = get_recipes_list(recipes_json)
    recipes_list = sorted(recipes_list, key=lambda x:x[0])
    n_recipes = len(recipes_list)  # 39774

    # Get ingredients list, sorted by id
    print "Processing ingredients"
    ingredients_list = get_ingredients_list(recipes_json)
    ingredients_list = sorted(ingredients_list, key=lambda x:x[0])
    n_ingredients = len(ingredients_list)  # 6714

    # Convert ingredients list to dict objects
    ings_id_name = {i[0]: i[1] for i in ingredients_list}
    ings_name_id = {i[1]: i[0] for i in ingredients_list}

    # Get dict object associating a single ingredient to recipes
    ing_recipes = get_ingredient_recipes(recipes_json, ings_name_id)

    # Get dict object associating a single recipe to ingredients
    rec_ingredients = get_recipes_ingredients(recipes_json, ings_name_id)

    # Get dict object associating ingredients
    ing_ingredients = get_ing_ingredients(ing_recipes, rec_ingredients)

    # Write to file
    "Writing to file"
    if n_args > 1:
        ingredients_network_filepath = args[1]
        ingredients_id_name_filepath = args[2]
        ingredients_name_id_filepath = args[3]
    else:
        output_folderpath = os.path.join(os.path.dirname(__file__), '../output')
        ingredients_network_filepath = os.path.join(output_folderpath, 'ingredients_network.json')
        ingredients_id_name_filepath = os.path.join(output_folderpath, 'ingredients_id_name.json')
        ingredients_name_id_filepath = os.path.join(output_folderpath, 'ingredients_name_id.json')

    # Write ingredients network to file
    with open(ingredients_network_filepath, 'wb+') as f:
        json.dump(ing_ingredients, f)
    # Write associations between ingredients id and name to file
    with open(ingredients_id_name_filepath, 'wb+') as f:
        json.dump(ings_id_name, f)
    # Write associations between ingredients name and id to file
    with open(ingredients_name_id_filepath, 'wb+') as f:
        json.dump(ings_name_id, f)


if __name__ == '__main__':
    n_args = len(sys.argv)
    if n_args > 1:
        write_ingredients_network(sys.argv[1:])
    else:
        print "Error: dataset file path not specified."