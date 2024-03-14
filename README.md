# Process modeling

## Task

`forth | stack | neum | hw | tick -> instr | struct | trap -> stream | port | pstr | prob5 | spi`

### Forth

Should use [Forth](https://forth-standard.org/): "An awesome stack based programming language, which is able to extend itself during runtime."

### Stack

Instead of registers uses stack

### Neumann

Uses von Neumann architecture: instructions and data shares memory

### Hardwired

Control unit is implemented inside model

### Instruction

Need to model with precision of 1 instruction

### Struct

Machine code should be in high-level structured file

### Stream

Input-output is stream of tokens. At the beginning there are all needed tokens

### Port-mapped IO

Should be special command to input and output data.

### Pascal strings

Strings should be length-prefixed

### Algorithm for testing purposes: [problem 5](https://projecteuler.net/problem=5). Smallest multiple

Task:
2520 is the smallest number that can be divided by each of the numbers from 1 to 10 without any remainder.
What is the smallest positive number that is evenly divisible by all the numbers from 1 to 20?

## Memory organisation

```
+----------------+
| 00: const data |
| ..             |
| n:  program    |
| ..   |         |
| ..   v         |
| ..             |
| ..   ^         |
| ..   |         |
| k:   stack     |
+----------------+
```


## [Translator](translator.md)

## [Emulator](emulator.md)

## Tests


| ФИО                       | <алг>      | <LoC> | <code байт> | <code инстр.> | <инстр.> | <такт.> | <вариант>                                                                                   |
|---------------------------|------------|-------|-------------|---------------|----------|---------|---------------------------------------------------------------------------------------------|
| Дзензелюк Илья Алексеевич | cat        | 1     | -           | 9             | 32       | 117     | `forth \| stack \| neum \| hw \| instr \| struct \| stream \| port \| pstr \| prob5 \| spi` |   
| Дзензелюк Илья Алексеевич | hello      | 1     | -           | 30            | 298      | 1557    | `forth \| stack \| neum \| hw \| instr \| struct \| stream \| port \| pstr \| prob5 \| spi` |   
| Дзензелюк Илья Алексеевич | hello_user | 1     | -           | 40            | 231      | 1140    | `forth \| stack \| neum \| hw \| instr \| struct \| stream \| port \| pstr \| prob5 \| spi` |   
| Дзензелюк Илья Алексеевич | prob5      | 3     | -           | 117           | 2107     | 10979   | `forth \| stack \| neum \| hw \| instr \| struct \| stream \| port \| pstr \| prob5 \| spi` |
