# foodgraph
This project analyzes the [food recipes' dataset provided by Kaggle](https://www.kaggle.com/c/whats-cooking).


## Data Processing
The input json file containing recipes and ingredients is loaded and processed. The complete list of ingredients is extracted from the recipes, then connections between ingredients contained in same recipes are found.  
  
Weights between connections are computed using a **"term frequency-inverse document frequency"** approach: a high number of recipes in common between ingredients results in a high weight score; conversely, if a single ingredient is associated with a high number of recipes, then the weight decreases.  
  
Finally, a graph is created using the above information. Each *node* of the graph represents an ingredient. Nodes are connected through an *edge* if they share recipes. The weight of each edge is calculated using the *tf-idf* method indicated.  
  
The analysis process was implemented in Python, the code being in the *src* folder. It can be executed using the Terminal command line:

```Shell
cd src/
python foodgraph.py ../dataset/kaggle_recipes.json ../output/nodes.csv ../output/edges.csv
```  
  
The arguments are:
  1. path to the input json file
  2. path to the output nodes' file
  3. path to the output edges' file
  
The output files contain 6715 (nodes) and 479922 (edges) rows.


## Graph Visualization and Analysis
The output files can be used to visualize the graph and analyze the information. [*Gephi*](http://gephi.org/) is the tool used in this case.  
  
![Graph Visualization](foodgraph.png)  
  
Some notes regarding the final output:
  - Ingredients included in less than 430 recipes (out of 39774) were removed from the graph
  - The size of each node is proportional to the number of recipes associated to it
  - Nodes' positions were defined using the Force Atlas algorithm, according to which nodes with higher weights and shared connections get closer to each other
  
A community-detection algorithm uncovered 5 clusters within the whole network. Each of them was assigned a specific color, can be located in a precise area of the plot and approximately linked to a culinary theme:
  1. green, South-West, desserts
  2. pink, North-West, Italian/Mediterranean
  3. blue, North-East, Mexican/Latin
  4. red, East, Indian
  5. purple, South-East, Asian