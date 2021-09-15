void main(void) {
__asm
main:
	mov p0,#0x00
	acall delay
	mov p0,#0xff
	acall delay
	ajmp	main
delay:
	mov r1,#04
d3:
	mov r2,#0xff
d2:
	mov r3,#0xff
d1:	djnz r3,d1
	djnz r2,d2
	djnz r1,d3
	ret
__endasm;
}


