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
//         goto LOOP2
//     else:
//         if color == 0:
//             goto LOOP1
//         color = 0

//     LOOP2:
//         if addr >= KBD goto LOOP1
//         RAM[addr] = color // 1..1
//         addr = addr + 1
//         goto LOOP2
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
            
            @LOOP2
            0;JEQ // goto LOOP2

        (COLOR_BLACK)
            @color
            D=M+1
            @LOOP1
            D;JEQ // if color == -1 goto LOOP1
            
            @color
            M=-1 // color = -1
        
        (LOOP2)
            @addr
            D=M
            @KBD
            D=D-A
            @LOOP1
            D;JGE // if addr >= KBD goto LOOP1

            @color
            D=M
            @addr
            A=M
            M=D // RAM[addr] = color
            
            @addr
            M=M+1 // addr = addr + 1

            @LOOP2
            0;JMP // goto LOOP2
