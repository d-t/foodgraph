# -*- coding: utf-8 -*-

from collections import Counter
import json


# ---------- Constants ---------- #

INPUT_FILEPATH = 'data/kaggle_recipes.json'
OUTPUT_FILEPATH = 'data/graph.json'


# ---------- Private Functions ---------- #

def _process_recipes(json_recipes):
    """
    Modify recipes dict: use recipe ids as keys.
    """
    recipes = {jr['id']: {'cuisine': jr['cuisine'], 
                          'ingredients': jr['ingredients']} \
               for jr in json_recipes}
    return recipes


def _process_ingredients(recipes):
    """
    Get ingredients dict.

    For each ingredient, generate a numeric id, get the list of recipes 
    containing it, count the list of cuisine styles of the associated recipes.
    """
    ingredients = {}
    counter = 0
    for r_id in recipes.keys():  # for each recipe id...
        curr_recipe = recipes[r_id]
        curr_ingredients = curr_recipe['ingredients']
        for ing in curr_ingredients:  # for each recipe ingredient...
            if ing not in ingredients:
                ingredients[ing] = {'recipes': [], 
                                    'cuisines': Counter(), 
                                    'id': str(counter)}
                counter += 1
            ingredients[ing]['recipes'].append(r_id)
            ingredients[ing]['cuisines'][recipes[r_id]['cuisine']] += 1
    return ingredients


def _get_ingredients_connections(ingredients, recipes):
    """
    Find connections between ingredients, i.e. ingredients sharing at least 
    one recipe
    """
    ing2ingredients = {}
    for i, ing_label in enumerate(ingredients.keys()):  # for each ingredient label...
        if i % 1000 == 0:
            print i, '/', len(ingredients.keys())
        ing = ingredients[ing_label]
        ing_id = ing['id']
        ing2ingredients[ing_id] = Counter()
        curr_recipes = ingredients[ing_label]['recipes']
        for r_id in curr_recipes:  # for each recipe id associated to the current ingredient...
            recipe = recipes[r_id]
            for curr_ingredient in recipe['ingredients']:  # for each ingredient included in the current recipe...
                if curr_ingredient != ing:  # ...if the ingredient is different from the first one...
                    ing_id_1 = ingredients[curr_ingredient]['id']
                    ing2ingredients[ing_id][ing_id_1] += 1  # ...increase the counter of the connection
    return ing2ingredients


def _create_graph(ingredients, ing2ingredients):
    """
    Create graph dict, final output.

    Each item is an ingredient, identified by a numeric id (in string format); 
    represents a graph node.
    Each item includes: edges, label, number of recipes containing the 
    ingredient, main cuisine.
    """
    graph = {}
    for ing_label in ingredients.keys():  # for each ingredient label...
        ing_id = ingredients[ing_label]['id']
        graph[ing_id] = {}
        graph[ing_id]['edges'] = ing2ingredients[ing_id].keys()
        graph[ing_id]['label'] = ing_label
        graph[ing_id]['n_recipes'] = len(ingredients[ing_label])
        curr_cuisines = ingredients[ing_label]['cuisines']
        main_cuisine_idx = curr_cuisines.values().index(max([curr_cuisines[r] \
                                                        for r in curr_cuisines]))
        graph[ing_id]['main_cuisine'] = curr_cuisines.keys()[main_cuisine_idx]
    return graph


# ---------- Public Functions ---------- #

def main():
    """
    Main function. Given a database of recipes, extract a graph of ingredients 
    and their connections.
    """
    global INPUT_FILEPATH, OUTPUT_FILEPATH

    # Load input file
    print "Load input file"
    filepath = INPUT_FILEPATH
    with open(filepath, 'rb') as f:
        json_recipes = json.load(f)

    # Get list of recipes
    print "Process recipes"
    recipes = _process_recipes(json_recipes)

    # Process ingredients
    print "Process ingredients"
    ingredients = _process_ingredients(recipes)

    # Find connections between ingredients
    print "Find connections between ingredients"
    ing2ingredients = _get_ingredients_connections(ingredients, recipes)

    # Create graph dict, final output
    print "Create graph object"
    graph = _create_graph(ingredients, ing2ingredients)
    
    # Write graph dict to json file
    output_filepath = OUTPUT_FILEPATH
    with open(output_filepath, 'wb+') as f:
        json.dump(graph, f, indent=2, sort_keys=True)


def main_cuisines(graph):
    """
    Analyze main cuisine values - just for fun.

    Count number of ingredients associated to each cuisine type.
    """
    main_cuisines = Counter()
    for ing_id in graph.keys():
        main_cuisines[graph[ing_id]['main_cuisine']] += 1

    # Sort by counter value
    print "Number of ingredients associated to each cuisine type"
    main_cuisines = [(cuisine, main_cuisines[cuisine]) for cuisine in main_cuisines.keys()]
    main_cuisines = sorted(main_cuisines, key=lambda x:x[1], reverse=True)

    # Print values
    for mc in main_cuisines:
        print mc[0] + ':', mc[1]


# ---------- ---------- #

if __name__ == '__main__':
    main()