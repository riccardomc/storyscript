Compiler
========
The compiler takes care of transforming the tree to a dictionary, line by line.
Additional metadata is added for ease of execution: the Storyscript version and
the list of services used by each story::

    {
        "stories": {
            "hello.story": {
                "tree": {...}
                "services": ["alpine"],
                "version": "0.0.15"
            },
            "foo.story": {
                "tree": {...},
                "services": ["twtter"],
                "version": "0.0.15"
            }
        },
        "services": [
            "alpine",
            "twitter"
        ],
        "functions": {
            "name": "line"
        }
    }

The compiled tree
------------------
The compiled tree uses a similar structure for every line::

    {
        "tree": {
            "line number": {
              "method": "operation type",
              "ln": "line number",
              "output": "if an output was defined (as in services or functions)",
              "service": "the name of the service or null",
              "command": "the command or null",
              "function": "the name of the function or null",
              "args": [
                "additional arguments about the line"
              ],
              "enter": "if defining a block (if, foreach), the first child line",
              "exit": "used in if and elseif to identify the next line when a condition is not met",
              "parent": "if inside the block, the line number of the parent",
              "next": "the next line to be executed"
            }
        }
    }

General properties
------------------
Method
######
The operation described by the line.

Ln
##
The line number.

Next
####
Next refers to the next line to execute. It acts as an helper, since the original
story might have comments or blank lines that are not in the tree, the next line
is not always the current line + 1

Parent
######
The parent property identifies nested lines. It can be used to identify all the
lines inside a block. Care must be taken for further nested blocks.


Objects
-------
Objects are seen in the *args* of a line. They can be variable names,
function arguments, string or numeric values::

    {
        "args": [
            {
                "$OBJECT": "objectype",
                "objectype": "value"
            }
        ]
    }

String
######
String object have a string property. If they are string templates, they will
also have a values list, indicating the variables to use when compiling the string::

    {
      "$OBJECT": "string",
      "string": "hello, {}",
      "values": [
        {
          "$OBJECT": "path",
          "paths": [
            "name"
          ]
        }
      ]
    }

List
####
Declares a list. Items will be a list of other objects::

    {
      "$OBJECT": "list",
      "items": [...]
    }

Dict
####
Declares an object::

    {
      "$OBJECT": "dict",
      "items": [
        [
          {
            "$OBJECT": "string",
            "string": "key"
          },
          {
            "$OBJECT": "string",
            "string": "value"
          }
        ]
      ]
    }

Type
####
Type objects declare the use of a type::

    {
      "$OBJECT": "type",
      "type": "int"
    }

Path
####

::

    {
        "args": [
            {
                "$OBJECT": "path",
                "paths": [
                    "varname"
                ]
            }
        ]
    }

Expression
##########
Expression have an expression property indicating the type of expression and
the two hand-sides of the expression in the values list. These will be two
other objects: paths or values::

    {
      "$OBJECT": "expression",
      "expression": "{} == {}",
      "values": [
          {
            "$OBJECT": "path",
            "paths": [
              "foo"
            ]
          },
          1
      ]
    }



Argument
########
Argument objects are used in function definition, function calls and services
to declare arguments:
::

    {
      "$OBJECT": "argument",
      "name": "id",
      "argument": {
        "$OBJECT": "type",
        "type": "int"
      }
    }


Method
######
Method objects is used when it's not possible to compile a tree that would
normally be a line as a proper line. For example, in `x = alpine echo`
the `alpine echo` bit would be compiled as method object::


    {
      "$OBJECT": "method",
      "method": "execute",
      "service": "alpine",
      "output": null,
      "args": [
        {
          "$OBJECT": "argument",
          "name": "pizza",
          "argument": {
            "$OBJECT": "string",
            "string": "please"
          }
        }
      ],
      "command": "echo"
    }

Methods
-------

Set
###
Used when declaring a variable, or assigning a value to a property::

    {
        "1": {
          "method": "set",
          "ln": "1",
          "args": [
            {
              "$OBJECT": "path",
              "paths": [
                "n"
              ]
            },
            1
          ],
          "next": "next line"
        }
    }

If
##
Args can be a path, an expression object or a pure value. When part of block of
conditionals, the exit property will refer to the next *else if* or *else*::

    {
      "method": "if",
      "ln": "1",
      "output": null,
      "service": null,
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "path",
          "paths": [
            "color"
          ]
        }
      ],
      "enter": "2",
      "exit": null,
      "parent": null,
      "next": "2"
    }

Elif
####
Similar to if::

    {
      "method": "elif",
      "ln": "3",
      "output": null,
      "service": null,
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "path",
          "paths": [
            "blue"
          ]
        }
      ],
      "enter": "4",
      "exit": null,
      "parent": null,
      "next": "4"
    }

Else
####
Similar to if and elif, but exit is always null and no args are available::

    {
      "method": "else",
      "ln": "5",
      "output": null,
      "service": null,
      "command": null,
      "function": null,
      "args": [],
      "enter": "6",
      "exit": null,
      "parent": null,
      "next": "6"
    }

For
###
Declares a for iteration::

    {
      "method": "for",
      "ln": "1",
      "output": [
        "item"
      ],
      "service": null,
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "path",
          "paths": [
            "items"
          ]
        }
      ],
      "enter": "2",
      "exit": null,
      "parent": null,
      "next": "2"
    }

Execute
#######
Used for services. Service arguments will be in *args*::

    {
      "method": "execute",
      "ln": "1",
      "output": [],
      "service": "alpine",
      "command": "echo",
      "function": null,
      "args": [
        {
          "$OBJECT": "argument",
          "name": "message",
          "argument": {
            "$OBJECT": "string",
            "string": "text"
          }
        }
      ],
      "enter": null,
      "exit": null,
      "parent": null
    }

Function
########
Declares a function. Output maybe null::

    {
      "method": "function",
      "ln": "1",
      "output": [
        "int"
      ],
      "service": null,
      "command": null,
      "function": "sum",
      "args": [
        {
          "$OBJECT": "argument",
          "name": "a",
          "argument": {
            "$OBJECT": "type",
            "type": "int"
          }
        },
        {
          "$OBJECT": "argument",
          "name": "b",
          "argument": {
            "$OBJECT": "type",
            "type": "int"
          }
        }
      ],
      "enter": "2",
      "exit": null,
      "parent": null,
      "next": "2"
    }

Return
######
Declares a return statement. Can be used only inside a function, thus will
always have a parent::

    {
      "method": "return",
      "ln": "2",
      "output": null,
      "service": null,
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "path",
          "paths": [
            "x"
          ]
        }
      ],
      "enter": null,
      "exit": null,
      "parent": "1"
    }


Call
####
Declares a function call, but otherwise identical to the execute method::


    {
      "method": "call",
      "ln": "4",
      "output": [],
      "service": "sum",
      "command": null,
      "function": null,
      "args": [
        {
          "$OBJECT": "argument",
          "name": "a",
          "argument": 1
        },
        {
          "$OBJECT": "argument",
          "name": "b",
          "argument": 2
        }
      ],
      "enter": null,
      "exit": null,
      "parent": null
    }
