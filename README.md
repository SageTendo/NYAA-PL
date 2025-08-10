# NYAA-PL (Not Yet Another Abstracted Programming Language)

## Introduction

NYAA-PL is a tree-walk interpreted programming language developed in Python (because why not :P),  
created for fun and exploration in the realms of language and compiler design. Inspired by  
anime, memes and the japanese language (borrowed and native words) references, this isn't  
intended for real-world use.

## Getting Started

### Prerequisites

- Python 3.10 🐍

## Features

#### Built-ins

- ##### yomu: print line to console
  ```python
  yomu("Hello, World!")
  ```
- ##### ohayo: get input from user
  ```python
  name = ohayo("Enter name: ")
  ```

#### Variables

```
name = "NYAA"
age = 1000
pi = 3.142

yomu(name)
yomu(age)
yomu(pi)
```

###### Output

```
NYAA
1000
3.142
```

#### Conditionals

- ##### if Statement
    ``` python
    # If statement
    nani ( expression ) { body }
    
    # If-else statement
    nani ( expression ) { body }
    baka { body }

    # If-elif statement
    nani ( expression ) { body }
    nandesuka ( expression ) { body }

    # If-elif-else statement
    nani ( expression ) { body }
    nandesuka ( expression ) { body }
    baka { body }
    ```    

- #### Loops
    ``` python
    # While loop
    daijoubu ( expression ) { body }
  
    # For loop
    # '_' can be used in the same way as a variable within the for loop
    for _ => ( start, end ) { body }
    for i => ( start, end ) { body }
    ```

#### Functions

- ##### Defining a function
  ###### Functions are defined before the program (main) block
  ```python
  # One line function
  kawaii func_name(param1, param2, ...) => statement 
  
  # Multi-line function
  kawaii func_name(param1, param2, ...) => { body } 
  ```
- ##### Calling a function
  ```python
  kawaii add(x, y) => {
    # return x + y 
    modoru x + y
  }
  
  uWu_nyaa() => {
    result = add(1, 1)
  }
  ```

## Code Examples

##### Hello_World.ny (single statement body)

```  
# program block  
uWu_nyaa() => yomu("Hello, world!");  
```  

##### Greet.ny

```  
# function definition  
kawaii greet(name) {
	yomu("Hello,", name)
}  
  
# program block  
uWu_nyaa() => {  
	# Get input from user and assign it to name
	name = ohayo("Enter name: ") 
	greet(name)
 }  
```

## Acknowledgements
