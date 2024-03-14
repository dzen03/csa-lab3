: gcd begin swap dup inc inc dup dec % dup until drop ;
: lcm dup dup dup inc inc inc swap * dec dec dec dec swap inc swap inc gcd swap / ;
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 begin swap dup if lcm else then dup until drop .
