#include <8052.h>
#include <stdio.h>
#include <math.h>

void UART_Init(int baudrate)
{ 
    PCON = 0x80;
    SCON = 0x50;  // Asynchronous mode, 8-bit data and 1-stop bit
    TMOD = 0x20;  //Timer1 in Mode2.

    TCON = 0;
    TH1 = 256 - (12000000UL)/(long)(16UL*12UL*baudrate) ; // Load timer value for baudrate generation
    TR1 = 1;      //Turn ON the timer for Baud rate generation
}
int putchar(int ch)
{
    SBUF = ch;      // Load the data to be transmitted
    while(TI==0);   // Wait till the data is trasmitted
    TI = 0;         //Clear the Tx flag for next cycle.
    return 0;
}
int getchar(void)
{
  while(RI==0);
  int ch = SBUF;
  RI = 0;
  return ch;
}
char line[40];
char ii=0;
void main(void)
{
    UART_Init(4800UL);
    while(1)
    {
      char ch=getchar();
      if(ch == 0xd){
        line[ii]=0x0;
        ii = 0;
        printf_tiny("%s\r\n",line);
      }else{
        line[ii++] = ch;
        printf_tiny("%c",ch);
      }
      
    }
}