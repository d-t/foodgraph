import csv
import json
import random

# TODO: handle "global" variables, e.g. ings_name_id


def get_correlated_ingredients(ing_name, is_output_id=True, n_links=5):
    """
    Given the name of an ingredient, randomly get correlated ones.

    Args:
        - ing_name: string containing the name of the input ingredient
        - is_output_id: Boolean value, if True then the output ingredients are 
                        represented by their ids; if False, by their names
        - n_links: integer representing the number of output associated ingredients to 
                   return

    Returns:
        - ings_linked: list containing correlated ingredients, represented either as 
                       numerical ids or string names

    TODO: get ingredients depending on stored weights.
    """

    # Check input
    n_links = int(n_links)

    # Get ingredient id
    ing_id = None
    if ing_name in ings_name_id:
        ing_id = ings_name_id[ing_name]
    else:
        ing_name = ing_name.lower()
        for i in ings_name_id:
            if i == ing_name:
                ing_id = ings_name_id[i]
        if ing_id is None:
            print "Error: ingredient not found."
            return -1

    # Get linked ingredients ids
    ings_linked_all = ing_ingredients[ing_id]
    n_ings_linked = len(ings_linked_all)

    # Retrieve ids of random linked ingredients
    if n_ings_linked < n_links:
        ings_linked_ids = ings_linked_all
    else:
        ings_linked_ids = []
        for i in xrange(n_links):
            ing_linked_id = ings_linked_all.keys()[random.randint(0, n_ings_linked - 1)]
            if ing_linked_id not in ings_linked_ids:
                ings_linked_ids.append(ing_linked_id)

    # Return list
    if is_output_id is False:  # if ids to be converted to names...
        ings_linked_names = []
        for ing_linked_id in ings_linked_ids:
            ings_linked_names.append(ings_id_name[ing_linked_id])
        ings_linked = ings_linked_names
    else:
        ings_linked = ings_linked_ids

    return ings_linked


def create_network(ing_name, network=None, n_links=5):
    """
    Create a network of associated ingredients.

    Args:
        - ing_name: string containing the name of the input ingredient
        - network: dict object with two keys:
                       - nodes: list of network nodes, i.e. ingredient ids
                       - edges: list of connections between nodes
                   If None, an empty dict will be created; otherwise the input object 
                   will be updated
        - n_links: integer representing the number of output associated ingredients to 
                   return

    Return:
        - network: dict object

    The function calls get_correlated_ingredients to get the ingredients associated to 
    the input, then checks if those ingredients are connected in the "global" network.
    """

    # Check input network
    if network is None:
        network = {}
        network['nodes'] = []
        network['edges'] = []

    # Convert input ingredient to id
    if ing_name in ings_name_id:
        ing_id = ings_name_id[ing_name]

    # Get correlated ingredients and add them to the nodes
    if ing_id not in network['nodes']:
        network['nodes'].append(ing_id)
    ings_correlated = get_correlated_ingredients(ing_name, is_output_id=True, n_links=n_links)
    for ic in ings_correlated:
        if ic not in network['nodes']:
            network['nodes'].append(ic)
    
    # Get edges
    n_nodes = len(network['nodes'])
    for n1 in xrange(n_nodes-1):
        node1 = network['nodes'][n1]
        for n2 in xrange(n1+1, n_nodes):
            node2 = network['nodes'][n2]
            if node1 != node2:
                if (node1, node2) not in network['edges']:
                    ings_associated = ing_ingredients[node1]
                    if node2 in ings_associated:
                        network['edges'].append((node1, node2))

    # Return updated network
    return network


def store_network(network, nodes_filepath='nodes.csv', edges_filepath='edges.csv', 
                  edges_type='Undirected'):
    """
    Store the ingredients network into two files, one for nodes and the other for edges.

    Args:
        - network: dict object with two keys:
                       - nodes: list of network nodes, i.e. ingredient ids
                       - edges: list of connections between nodes
        - nodes_filepath: string representing the path where the nodes file needs to be 
                          stored
    """

    # Nodes
    nodes = network['nodes']
    output_nodes = [['Id', 'Label']]
    for node in nodes:
        node_id = node
        if node_id in ings_id_name:
            node_label = ings_id_name[node_id]
            output_nodes.append([node_id, node_label])
    with  open(nodes_filepath, 'wb+') as f:
        csv_writer = csv.writer(f, delimiter='\t')
        csv_writer.writerows(output_nodes)

    # Edges
    edges = [['Source', 'Target', 'Type']]
    for edge in network['edges']:
        source = edge[0]
        target = edge[1]
        if source in nodes and target in nodes:
            edges.append([source, target, edges_type])
    with open(edges_filepath, 'wb+') as f:
        csv_writer = csv.writer(f, delimiter='\t')
        csv_writer.writerows(edges)