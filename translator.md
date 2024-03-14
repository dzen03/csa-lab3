# Translator

[Source code](translator.py)

```
program ::= word

word ::= number
       | symbol
       | string
       | if
       | loop
       | function
       | word word
       | "DUP" | "SWAP" | "DROP" | "HALT" | "=" 
       | "+" | "-" | "*" | "/" | "%" | "DEC" | "INC"
       | "." | "INPUT" | ".s"

number ::= [0-9]+
symbol ::= '[a-zA-Z]'
string ::= ."[a-zA-Z ]*"
if ::= "IF" word "ELSE" word then 
loop ::= "BEGIN" word "UNTIL"
function ::= ":" word ";"
```

## Predefined words aka commands

- `DUP` duplicates the top of stack (TOS)
- `SWAP` interchanges the top two elements
- `DROP` pops the TOS discarding it
- `HALT` stops everything _(not an actual Forth word)_
- `=` pops the top two elements, compares them, and pushes 1 onto the stack if there are equal/less/greater, and 0 if not
- `+ - * / %` pops the top two elements, does math and pushes result back onto the stack
- `:` defines a new word (see [this](#defining-words-aka-functions))
- `DEC` decreases stack pointer
- `INC` increases stack pointer

### Words for IO and memory manipulation _(non Forth)_

- `.` pops and prints the TOS
- `INPUT` pushes char from user to the TOS
- `.s` pops entire string
- `."string"` prints string to output

## Loops

`BEGIN words UNTIL` - doing `words` until 0 happens on stack on check; then goes to the next word after `BEGIN`

## Conditions

```
IF words ELSE words THEN
```

## Defining words aka functions

```
: name words ;
```

Creates a word called `name` that, upon execution, executes all `words`

## Commands system

### Predefined words

- .s `: .s begin swap . 1 swap - dup until ;`
- drop `: drop inc ;`
- swap `: swap dup inc - dup dec - dup inc + dec ;`

Correction check on swap:

```
a b -> a a b -> a | a b -> a a | a-b -> a | a-b a-b -> a a-b a-b -> b a-b -> b b a-b -> b | b a-b -> b | a -> b a
    -> dup   -> inc     -> -         -> dup         -> dec       -> -     -> dup     -> inc       -> +     -> dec
```

### if - else - then

| Position | source code | machine code |
|----------|-------------|--------------|
| n        | `if`        | `jz m`       |
| ...      | ...         | ...          |
| ...      |             | `jmp k`      |
| m        | `else`      |              |
| ...      | ...         | ...          |
| k        | `then`      |              |

### begin - until

| Position | source code | machine code |
|----------|-------------|--------------|
| n        | `begin`     |              |
| ...      | ...         |              |
| ...      |             | `jz m + 1`   |
| m        | `until`     | `jmp n`      |
