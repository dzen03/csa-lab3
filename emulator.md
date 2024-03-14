# Hardware
[Source code](emulator.py)

## Control path
```
                                                                        sel_inp          cu_output         
                                                                          |               ^      user_output
                                                                cu_input  |  user_input   |   +-------->   
                                                                   |      |      |        |   |            
                                                                   |      |      |        |   |            
                                                                   |      |      |        |   |            
                                                                   |      |      |        +---+
   latch_rbp                                                       |      |      |        |MUX|<--sel_out
       |                                                           |      v      |        +-+-+           
       |                                       sel_addr            |    +---+<---+          ^              
       v                                          |                +--->|MUX|               |              
    +-----+                                       |                     +-+-+<---+---+      |              
+---| rbp |<------------+    instruction_addr     |                       |      |acc|<-----+              
|   +-----+             |    ------------------+  |                       |      +---+      |              
| latch_stack_pointer   |                      v  v        +---------+    |        ^        |              
|  ----------------->+---------------+        +-----+      | data    |    |        |        |              
|                    | stack_pointer +---+--->| MUX +----->|         | in |    latch_acc    |              
*-----------v        +---------------+   |    +-----+      | stack & +<---+                 |              
  sel--->+--+--+        ^                |                 | program |                      |              
         | MUX |--------+                |                 |         | out                  |              
    +--->+-----+                         |                 |         +----------------------+     
    |     ^   ^                          |                 |         |                      |              
    |     |   |   +1                     |                 |         |oe                    |              
    |     |   +--------------------------+                 |         |<--                   |               
    |     |   -1                         |                 |         |we                    |              
    |     +------------------------------+                 |         |<--                   |                    
    |                                                      +---------+                      |
    +---(stack addr select)-----------------------------------------------------------------+              
```
acc used only for dup

rbp to move back to original stack_pointer state

## Control unit
```
  +-------+                                            
  |       |                                            
  |    +--+------+                                     
  |    | program |       instruction_addr              
  |    | counter +------------------------------------+
  |    +---------+                                    |
+1|         ^                           +---------+   |
  |         |                     +-----+ step    |   |
  |      +--+--+                  |     | counter |   |
  |      | MUX |  sel_next        |     +---------+   |
  +----->+-----+<--------+        v             ^     |
            ^            +-------------+        |     |
            |            |             |        |     |
            |            | instruction +--------+     |
            +----------->|   decoder   |              |
            |cu_output   |             |              |
            |            +--+----------+              |
            |               |                         |
            |               |signals                  |
            |               v                         |
            |             +----------+                |
            +-------------+          |<---------------+
                          | DataPath |                 
                          |          |                 
                 -------->+----------+-------->        
                 input                 output          
```

## Instruction set

| word     | instruction   | ticks | description |
|----------|---------------|-------|-------------|
| =        | EQ            | 6     |             |
| +        | ADD           | 6     |             |
| -        | SUB           | 6     |             |
| *        | MUL           | 6     |             |
| /        | DIV           | 6     |             |
| %        | MOD           | 6     |             |
| dup      | DUP           | 5     |             |
| .        | OUTPUT        | 2     |             |
| input    | INPUT         | 2     |             |
| dec      | DEC           | 1     |             |
| inc      | INC           | 1     |             |
|          | MOV <addr>    | 1     |             |
|          | MOV_RBP       | 1     |             |
| <number> | PUSH <number> | 2     |             |
|          | JMP           | 1     |             |
|          | JZ            | 2     |             |
|          | HALT          | -     |             |

### +3 translation time defined:
#### .s

`: .s begin swap . until ;`

#### drop

`: drop inc ;`

#### swap

`: swap dup dup dec dec - dup inc + dup dup dec dec - -1 * inc ;`

## Encoding:
Machine code serializes to JSON with static_data in front.

