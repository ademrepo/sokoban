


# **Project 1** 

# **Modeling and solving the Sokoban Puzzle** 

<mark>Sokoban (Pushbox) is a classic puzzle game, originating from Japan and dating back to the early 1980s. In this game, a warehouse keeper (the player) moves around a warehouse, represented by a grid of squares. These squares are of five types: PLAYER, WALL, EMPTY SPACE, BOX, TARGET SPACE (see Figure 1). The goal of the game is to place all the boxes on the target spaces.</mark> 



<mark>The rules of the game are very simple:</mark> 

- ⚫ <mark>The structure of the warehouse and the number of boxes vary from one level to another.</mark> 

- ⚫ <mark>The warehouse in which the boxes must be placed rarely has the shape of a simple rectangle; it is more of a maze, more or less complicated. There are walls on all sides of this maze.</mark> 

- ⚫ <mark>There can be one or more boxes, and there are always as many target spaces as there are boxes.</mark> ⚫ <mark>The game has only one player, who can move in the four cardinal directions.</mark> 

- ⚫ <mark>The player is only allowed to move to an unoccupied space (one that is not a wall) or push a box and move onto the free space. They are not allowed to pull a box or move over it.</mark> 

- ⚫ <mark>To push a box, the space adjacent to the box in the direction of the push must be free. The player cannot push two boxes at the same time.</mark> 


- ⚫ <mark>The player wins when all the boxes are on the target spaces, in any order. There are no boxes assigned to specific target points.</mark> 

<mark>The objective of the project is first to model the game, then implement a solver based on various search algorithms, and finally create a GUI for this game.</mark> 

## **A.** **<u>Problem formulation:</u>** 

The first step in this assignment is to propose a formulation for the Sokoban game, and implement it in Python. 

## **1. Modeling the state:** 

To model a state, the following instructions must be followed: 

- ⚫ The game is presented in the form of a two-dimensional grid. We need to be able to represent the following elements: walls, empty spaces, and target spaces, which are static elements, as well as the player and the boxes, which are dynamic elements. In this grid, we can have squares with the following configurations (see Figure 2): 

Figure 2 Configuration of a Sokoban board 

- Player (Robot): represented by 'R' 

- Wall (Obstacle): represented by 'O' 

- Empty space: represented by '   ' 

- Target space (Storage): represented by 'S' 

- Box (Block): represented by 'B' 

- Player on a target space: '.' 

- Box on a target space: '*' 

- ⚫ To move from one state to another, the player must move within the grid. Four movements are allowed: 

Dr. Meriem SEBAI, USTHB 

2 

- UP: (-1, 0) 

- DOWN: (1, 0) 

- LEFT: (0, -1) 

- RIGHT: (0, 1) 

- ⚫ For a move to be valid, it must follow the game's rules (see the game description).  The goal state is reached when all the boxes are on the target spaces. 

To model a state in the Sokoban game, we define the class **SokobanPuzzle** with the following functions: 

- _init()_ : This function creates a state. 

- _isGoal( )_ : This function checks if a state is a goal. 

- _successorFunction( )_ : This function generates pairs of ( _action_ , _successor_ ) representing all possible moves that can be applied on the board. 

## **2. Modeling the node:** 

The **Node** class should include the following components: 

- _state_ : An instance of the **SokobanPuzzle** class representing the state; 

- _parent_ : A reference to the parent node; 

- _action_ : The action applied to generate the current node from the parent node; 

- _g_ : The path cost, where the step cost _c_ is always equal to 1; 

In the **Node** class, you should also provide definitions for the following functions: 

- _getPath ( )_ : This function returns a list or sequence of states representing the path from the initial state to the goal state of the solution; 

- _getSolution ( )_ : This function returns a list or sequence of actions applied to the initial state to reach the goal state; 

## **B.** **<u>Searching for a solution:</u>** 

The next step in this assignment is to solve the Sokoban puzzle using the Breadth-First Search (BFS) algorithm. Utilize the provided pseudocode from the course to create an implementation of the BFS algorithm. 

## **C.** **<u>Game interface:</u>** 

Create an interface in Pygame that displays a simulation of the solution found, its cost, and the number of steps taken by the different search algorithms. 
