// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
// ----------------- pseudo code start -----------------
// color = 0
// LOOP1:
//     M[addr] = SCREEN
    
//     if M[KBD] > 0:
//         if color == -1:
//             goto LOOP1
//         color = -1
//         goto START_FILLING
//     else:
//         if color == 0:
//             goto LOOP1
//         color = 0

//     START_FILLING:
//         iter = 1
//         fill_every_ith_mem = 4 // 2th power is recommended

//         LOOP2:
//             if addr >= KBD goto CHECK_ITER
//             RAM[addr] = color // 1..1(0..0)
//             addr = addr + fill_every_ith_mem
//             goto LOOP2

//             CHECK_ITER:
//                 if iter >= fill_every_ith_mem goto LOOP1
//                 addr = SCREEN + iter
//                 iter = iter + 1
//                 goto LOOP2
// ----------------- pseudo code end -------------------

(MAIN)
    @color
	M=0 // color = 0
	
    (LOOP1)
        @SCREEN
        D=A
        @addr
        M=D // addr = 16384
        
        @KBD
        D=M
        @COLOR_BLACK
        D;JGT // if RAM[KBD] > 0 goto COLOR_BLACK

        (COLOR_WHITE)
            @color
            D=M
            @LOOP1
            D;JEQ // if color == 0 goto LOOP1
            
            @color
            M=0 // color = 0
            
            @START_FILLING
            0;JEQ // goto LOOP2

        (COLOR_BLACK)
            @color
            D=M+1
            @LOOP1
            D;JEQ // if color == -1 goto LOOP1
            
            @color
            M=-1 // color = -1
        
        (START_FILLING)
            @iter
            M=1 // iter = 1

            @4
            D=A
            @fill_every_ith_mem
            M=D // fill_every_ith_mem = 4 (2th power is recommended)

            (LOOP2)
                @addr
                D=M
                @KBD
                D=D-A
                @CHECK_ITER
                D;JGE // if addr >= KBD goto CHECK_ITER

                @color
                D=M
                @addr
                A=M
                M=D // RAM[addr] = color
                
                @fill_every_ith_mem
                D=M
                @addr
                M=M+D // addr = addr + fill_every_ith_mem

                @LOOP2
                0;JMP // goto LOOP2

                (CHECK_ITER)
                    @iter
                    D=M
                    @fill_every_ith_mem
                    D=D-M
                    @LOOP1
                    D;JGE // if iter >= fill_every_ith_mem goto LOOP1

                    @SCREEN
                    D=A
                    @iter
                    D=D+M
                    @addr
                    M=D // addr = @SCREEN + iter

                    @iter
                    M=M+1 // iter = iter + 1

                    @LOOP2
                    0;JMP
