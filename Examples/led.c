#include <8052.h>
#include <stdio.h>

void UART_Init(int baudrate)
{ 
    PCON = 0x80;
    SCON = 0x50;  // Asynchronous mode, 8-bit data and 1-stop bit
    TMOD = 0x20;  //Timer1 in Mode2.

    TCON = 0;
    TH1 = 256 - (12000000UL)/(long)(16UL*12UL*baudrate) ; // Load timer value for baudrate generation
    TR1 = 1;      //Turn ON the timer for Baud rate generation
    TI = 1;
    RI = 1;
}
int putchar (int c) {
  while (!TI) /* assumes UART is initialized */
    ;
  TI = 0;
  SBUF = c;
  return c;
}

void main(void)
{
    int counter=0;
    int base=0;

    int duty=0;
    int duty_slope=1;
    int state=1;
    short pattern=1;
    int direction=1;
    UART_Init(4800);
    while(1)
    {
        if(counter % 5000 ==0){
            if(state == 1) state = 2;
            else if(state == 2) state = 1;
            else state = 1;
            printf_tiny("lalala\n");
        }
        if(state == 1){
            if(counter % 1 == 0){
                base += 1;
                if(base == 10) base = 0;

            }
            if(counter % 100 == 0){
                duty += duty_slope;
                if(duty == 10) duty_slope = -1;
                if(duty == 0) duty_slope = 1;
            }
            if(base > duty) 
                P0 = 0x00; // Turn ON all LED's connected to Port1
            else 
                P0 = 0xff; // Turn OFF all LED's connected to Port1
        }
        if(state == 2){
            if(counter % 100 == 0){  
                P0 = ~pattern;
                if(direction == 1){
                    pattern = pattern << 1;
                    if(pattern == 0x80) direction = 2;
                }
                else if(direction == 2){
                    pattern = pattern >> 1;
                    if(pattern == 0x01) direction = 1;
                }
                else
                    direction = 1;
            }
        }
        counter++;
    }
}





