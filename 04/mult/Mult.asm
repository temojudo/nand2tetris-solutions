// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
// ----------------- pseudo code start -----------------
// a = R0
// b = R1
// i = 1
// ans = 0

// LOOP:
//     if i > a goto STOP
//     ans = ans + b
//     i = i + 1
//     goto LOOP
// STOP:
//     R2 = ans
// ----------------- pseudo code end -------------------

(MAIN)
	@R0
	D=M
	@a
	M=D // a = R0

	@R1
	D=M
	@b
	M=D // b = R1
	
	@R2
	M=0 // M[2] = 0

	@i
	M=1 // i = 1
	@ans
	M=0 // ans = 0
	
	(LOOP)
		@i
		D=M
		@a
		D=D-M
		@STOP
		D;JGT // if i > a goto STOP
		
		@ans
		D=M
		@b
		D=D+M
		@ans
		M=D // ans = ans + b
		
		@i
		M=M+1 // i = i + 1
		
		@LOOP
		0;JMP
	
	(STOP)
		@ans
		D=M
		@R2
		M=D // RAM[2] = ans

	(END)
		@END
		0;JMP
