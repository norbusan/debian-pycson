[![Build Status](https://travis-ci.org/avakar/pycson.svg?branch=master)](https://travis-ci.org/avakar/pycson)

# pycson

A python parser for the Coffeescript Object Notation (CSON).

## Installation

The parser is tested on Python 2.7 and 3.4.

    pip install cson

The interface is the same as for the standard `json` package.

    >>> import cson
    >>> cson.loads('a: 1')
    {'a': 1}
    >>> with open('file.cson', 'rb') as fin:
    ...     obj = cson.load(fin)
    >>> obj
    {'a': 1}

## The language

There is not formal definition of CSON, only an informal note in [one project][1]'s readme.
Informally, CSON is a JSON, but with a Coffeescript syntax. Sadly [Coffescript][2] has no
format grammar either; it instead has a canonical implementation.

This means that bugs in the implementation translate into bugs in the language itself.

Worse, this particular implementation inserts a "rewriter" between the typical
lexer/parser pair, purporting that it makes the grammar simpler. Unfortunately, it adds
weird corner cases to the language..

This parser does away with the corner cases,
in exchange for changing the semantics of documents in a few unlikely circumstances.
In other words, some documents may be parsed differently by the Coffescript parser and pycson.

Here are some important highlights (see the [formal grammar][3] for details).

 * String interpolations (`"#{test}"`) are allowed, but are treated literally.
 * Whitespace is ignored in arrays and in objects enclosed in braces
   (Coffeescripts requires consistent indentation).
 * Unbraced objects greedily consume as many key/value pairs as they can.
 * All lines in an unbraced object must have the same indentation. This is the only place
   where whitespace is significant. There are no special provisions for partial dedents.
   For two lines to have the same indent, their maximal sequences of leading spaces and tabs
   must be the same (Coffescript only tracks the number of whitespace characters).
 * Unbraced objects that don't start on their own line will never span multiple lines.
 * Commas at the end of the line can always be removed without changing the output.

I believe the above rules make the parse unambiguous.

This example demonstrates the effect of indentation.

    # An array containing a single element: an object with three keys.
    [
      a: 1
      b: 2
      c: 3
    ]

    # An array containing three elements: objects with one key.
    [
      a: 1
       b: 2
      c: 3
    ]

    # An array containing two objects, the first of which having one key.
    [ a: 1
      b: 2
      c: 3 ]

Note that pycson can parse all JSON documents correctly (Coffeescript can't because
of whitespace and string interpolations).

  [1]: https://github.com/bevry/cson
  [2]: http://coffeescript.org/
  [3]: grammar.md
