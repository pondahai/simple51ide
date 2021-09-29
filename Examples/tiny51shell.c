//#include <8052.h>
#include <at89x52.h>
#include <stdio.h>
#include <math.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>

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
char line[20];
__idata char pool[80]={0};
char ii=0;
char debug=0;
char process (char *s)  
{
  __idata char oprand[8][8]={"","","","","","","",""};
  char si=0;
  char oc=0;
  char osi=0;
  char state=0;
  char quote_count=0;
  //
  // parsing
  //
  while(s[si]){
    char c = toupper(s[si]);
    // line number parsing
    if(state == 0){ // leading space strip off
      if(c==' ') {si++; continue;}
      if(isdigit(c)) {oprand[oc][osi++]=c; state=1; si++; continue;}
      else {oprand[oc][osi++]=c; state=2; si++; continue;} // leading not number
    }
    if(state == 1){ // line number
      if(c==' ') {oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(isdigit(c)) {oprand[oc][osi++]=c; state=1; si++; continue;}
      else return si; // line number syntax error
    }
    if(state == 2){ // 
      if(c=='"') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='"'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; if(quote_count==0)quote_count=1; else quote_count=0; continue;}
      // do not process betreen quotes
      if(quote_count>0){if(quote_count > 7){state=2; si++; continue;} quote_count++; oprand[oc][osi++]=c; state=2; si++; continue;}
      // space
      if(c==' '){if(osi==0){si++; continue;}else{oprand[oc][osi++]=0x0; osi=0; oc++; state=2; si++; continue;}}
      // number
      if(isdigit(c)) {
        if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]=c; state=3; si++; continue;
      }
      //
      if(c=='+') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='+'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='-') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='-'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='*') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='*'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='/') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='/'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='=') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='='; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='(') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='('; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c==')') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]=')'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      // other keyword
      oprand[oc][osi++]=c; state=2; si++;
    }
    if(state == 3){ // number process
      if(isdigit(c)) {oprand[oc][osi++]=c; state=3; si++; continue;}
      else {
      // space
      if(c==' '){if(osi==0){si++; continue;}else{oprand[oc][osi++]=0x0; osi=0; oc++; state=2; si++; continue;}}
      if(c=='+') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='+'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='-') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='-'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='*') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='*'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='/') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='/'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='=') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='='; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c=='(') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]='('; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      if(c==')') {if(osi!=0){oprand[oc++][osi++]=0x0; osi=0;} oprand[oc][osi++]=')'; oprand[oc][osi++]=0x0; oc++; osi=0; state=2; si++; continue;}
      // other keyword
      oprand[oc++][osi++]=0x0; osi=0; oprand[oc][osi++]=c; state=2; si++;        
      } 
    }    

     
  }// while parsing
  oprand[oc][osi++]=0x0;
  
  // if the quotes are not paired
  if(quote_count) return 0;  

  if(debug){  
    for(char i=0;i<8;i++)
      printf_tiny("%d_%s ",i,oprand[i]);
    printf_tiny("\r\n");
  }
  //
  // excute
  //
  if (isdigit(oprand[0][0])){
    // line number
    // convert it into pool
    char pi=0;
    oc=0;
    
    while(1){
      if(pool[pi]==0x0){ // meet 0x0
      
    
        if(pi!=0x0){pi++;} // if not head, skip 0x0
        if(pool[pi]!=0x0){ pi++;if(pi==32){ break;}else{ continue;}}
        
          pool[pi++]=(char)atoi(oprand[oc++]); // insert line number
        
          if(strcmp(oprand[oc],"PRINT")==0) { // insert PRINT and string
            oc++;
            pool[pi++]=0x01;                  // insert PRINT opcode number
            
            if(strcmp(oprand[oc++],"\"")==0) {            // it is string
              strcpy(&pool[pi],oprand[oc++]);  // insert string into pool
            }
            
          }
          if(strcmp(oprand[oc],"RUN")==0) { // 
            oc++;
            pool[pi++]=0x02;                  // 
          }          
          if(strcmp(oprand[oc],"FOR")==0) { // 
            pool[pi]=0x03;                  //
            strcpy(&pool[pi+3],oprand[oc+1]); // variable name
            pool[pi+1]=(char)atoi(oprand[oc+3]);
            pool[pi+2]=(char)atoi(oprand[oc+5]);
            oc+=5;
            pi+=4;
          }          
          if(strcmp(oprand[oc],"NEXT")==0) { // 
            pool[pi]=0x04;
            strcpy(&pool[pi+1],oprand[oc+1]); // variable name
            oc+=2;
            pi+=2;
          }
        oc++;
        if(oc == 8){ break;}
        if(oprand[oc][0] == 0x0){ break;}        
      }else{
        pi++;
        if(pi==32){ break;}
      }
    }
    
  }else{
    // intepretor
    if(strcmp(oprand[0],"PRINT")==0){
      if(strcmp(oprand[1],"\"")==0){
        printf_tiny("%s\r\n",oprand[2]);
      }
    }
    if(strcmp(oprand[0],"DEBUG")==0){
      debug=~debug;
    }
    if(strcmp(oprand[0],"NEW")==0){
      for (char i=0;i<80;i++) {pool[i]=0x0;}
    }
    //
    if(strcmp(oprand[0],"LIST")==0){
     if(debug){
      char memcnt=0;
      for (char i=0;i<80;i++){
        if(pool[i] == 0x0) {printf_tiny("0 "); continue;}
        printf_tiny("%x ",pool[i]);
        memcnt++;
      }
      printf_tiny("\r\n%d\r\n",memcnt);
      printf_tiny("\r\n");
     }
      for (char i=0;i<80;i++){
        if(pool[i] == 0x0) continue;
        printf_tiny("%d ", pool[i]);
        if(pool[i+1]==0x1){ // PRINT
          printf_tiny("PRINT \"%s\"\r\n", &pool[i+2]);
          i+=2;
        }
        if(pool[i+1]==0x3){ // FOR
          printf_tiny("FOR %s = %d TO %d\r\n", &pool[i+4], pool[i+2], pool[i+3]);
          i+=4;
        }
        if(pool[i+1]==0x4){ // NEXT 
          printf_tiny("NEXT %s\r\n", &pool[i+2]);
          i+=2;
        }
        if(pool[i+1]==0x2){ // RUN
          printf_tiny("RUN\r\n");
          i+=1;
        }
        while(pool[++i]!=0x0);
      }       
      printf_tiny("\r\n");
    } // LIST
    //
    if(strcmp(oprand[0],"RUN")==0){
      for (char i=0;i<80;i++){
        if(pool[i] == 0x0) continue;
        
        if(pool[i+1]==1){ // PRINT
          printf_tiny("%s\r\n", &pool[i+2]);
          i+=2;
        }
        if(pool[i+1]==2){ // RUN
          i=0xff;
          continue;
        }
        while(pool[++i]!=0x0);
      }       
      printf_tiny("\r\n");      
    }// RUN
  } //
  
  return -1;
}
void main(void)
{
    UART_Init(4800UL);
    while(1)
    {
      char ch=getchar();
      if(ch == 0xd){
        line[ii]=0x0;
        ii=0;
        printf_tiny("\r\n");
        char err=process(line);
        //printf_tiny("%d\n",err);
        if(err != 255){
          for(char i=0;i<err;i++)
            printf_tiny(" ");
          printf_tiny("^\r\n");
        }
        ii=0;
        /*
        while(1){
          char c=line[ii++];
          if(c==0x0) break;
          printf_tiny("%x ",c);
        }
        */
        printf_tiny("\r\n");
        ii=0;
        //printf_tiny("%s\r\n",line);
      }else{
        line[ii++] = ch;
        printf_tiny("%c",ch);
      }
      
    }
}