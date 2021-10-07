#include <8052.h>
//#include <at89x52.h>
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
#define LINE_LENGTH 30
char line[LINE_LENGTH];
__idata char pool[80]={0};
char debug=255;
// 
__idata char ff[3]={0}; // for loop variable's fifo
char ffi=0xff;
//
// intepreter
// return:
// 0: have no keyword
// 1~8: keyword finish
// 253: next byte
// 254: list
// 255: running
// 
char intepreter(char *s, char list_run, char now_i){
  char i=0;
  
  //printf_tiny("SP=%d\r\n",SP); 
  
    if(list_run==0){
      // list mode
      s--; // pointer backward one byte to get line number
      // line number
      if(s[i]){ printf_tiny("%d ", s[i]);}
      i++;
    }else{
      // running mode
      if(s[i] == 0x0) return 253;
      if(debug){printf_tiny("%s\r\n",s);}
    }
    if(s[i]==0x1){ // PRINT  LL 01 AA .. AA 00
      if(list_run==0){ // list
        printf_tiny("PRINT \"%s\"\r\n", &s[i+1]);
        i+=1+strlen(&s[i+1]);
      }
      if(list_run==1){ // 
          printf_tiny("%s\r\n", &s[i+1]);
          i+=1+strlen(&s[i+1])+1;
          //i=0;
      }
      return now_i+i;
    }
    if(s[i]==0x2){ // RUN    LL 02 00
      if(list_run==0){
        printf_tiny("RUN\r\n");
        i+=1;
      }
      if(list_run==1){ // 
          //i=0xff;
          return 255;
      }
      return now_i+i;
    }
    if(s[i]==0x3){ // FOR    LL 03 XX YY II AA .. AA 
      if(list_run==0){
        printf_tiny("FOR %s = %d TO %d\r\n", &s[i+4], s[i+1], s[i+2]);
        i+=4+strlen(&s[i+4]);
      }
      if(list_run==1){ // 
          s[i+3]=s[i+1];
          i+=4+strlen(&s[i+4])+1;
          //i=0;
      }
      return now_i+i;
    }
    if(s[i]==0x4){ // NEXT   LL 04 @@ AA .. AA 00 
      if(list_run==0){
        printf_tiny("NEXT %s\r\n", &s[i+2]);
        i+=2+strlen(&s[i+2]);
      }
      if(list_run==1){ // 
          char ti=s[i+1];
          if(debug){printf_tiny("%x\r\n",ti);}
          pool[ti]++;
          if(debug){printf_tiny("%x\r\n",pool[ti]);}
          if(pool[ti] < pool[ti-1]){return ti+1+1+strlen(&pool[ti+1]);} // move pointer to FOR line 
          //else i=0;// 
          else{i+=2+strlen(&s[i+2])+1;}
      }
      return now_i+i;
    }
    if(s[i]==0x5){ // POKE  LL 05 AD DA 00
      if(list_run==0){
        printf_tiny("POKE %d,%d\r\n", s[i+1], s[i+2]);
        i+=2+1;
      }
      if(list_run==1){ // 
          if(s[i+1] == 0x80) P0=s[i+2];
          i+=2+1+1;
          //i=0;
      }
      return now_i+i;
    }
    if(s[i]==0x6){ // LIST  LL 06 00
      if(list_run==0){
        printf_tiny("LIST\r\n");
        i+=1;
      }
      if(list_run==1){ // 
        return 254;
        //return 0;
      }
      return now_i+i;
    }
    if(s[i]==0x7){ // DEBUG LL 07 00
      if(list_run==0){
        printf_tiny("DEBUG\r\n");
        i+=1;
      }
      if(list_run==1){ // 
        debug=~debug;
        i+=1+1;
        //i=0;
      }
      return now_i+i;
    }
    if(s[i]==0x8){ // NEW   LL 08 00
      if(list_run==0){
        printf_tiny("NEW\r\n");
        i+=1;
      }
      if(list_run==1){ // 
        for (char i=0;i<80;i++) {pool[i]=0x0;}
        i+=1+1;
        //i=0;
      }
      return now_i+i;
    }    
    return 0;
}
void single_run(char *s) {
  char result=0;
  // single run
  for(char j=1;j<80;j++){
    result = intepreter(&s[j], 1, j); // single run
    if(result==0){break;}
    if(result==253){continue;} // it is 0x0
    if(result==255){break;}
    if(result==254){break;}
    //j+=result;
    if(result){j=result;}
    if(debug){
      printf_tiny("%d ",result);
    }
  }

  if(result==0){return; }
  // pool list or pool run
  //for(char j=0;j<80;j++){
    if(result==255){
      // running
      s=pool;
      for (char i=1;i<80;i++){
        result=intepreter(&s[i], 1, i);
        //if(result==0){break;} // normal finish
        if(result==255){i=0xff; continue;} // run from head
        //if(result==254){break;} // change to list
        if(result==253){break;}
        if(debug){
          printf_tiny("%d\r\n",result);
        }
        if(result){i=result;}
        // i+=result;
      } 
      //if(result==254){j=0xff; continue;}
      //break;     
    }
    else if(result==254){
      // list
      s=pool;
      for (char i=1;i<80;i++){
        result=intepreter(&s[i], 0, i);    
        //if(result==0){break;} // normal finish
        if(debug){
          if(result){ printf_tiny("list intepreter result: %d\r\n",result);}
        }
        if(result){i=result;}
        //i+=result;
      }
      //break;            
    }
    else if(result==0){
      //break;
    }
  //}
}
char process(char *s) {
  char pooli=0; 
  char si=0; // source index
  char pri=0; // parsing result index
  char i;
  char result;
  char length;
  char *from;
  char *to;
  if(strlen(&s[1])==0){return 0;}
  for(si=0;si<LINE_LENGTH;si++){
    s[si]=toupper(s[si]);    
  }
  for(si=1;si<LINE_LENGTH;si++){
    if(s[si]==' '){ continue;}
    if(isdigit(s[si])==0){ break;}
  }
  //printf_tiny("si=%d pi=%d\r\n",si,pri);
  //if(si>0){
    // it is line number if result is >0 and convert it
    result=0;
    for( i=0;i<si;i++){
      if(s[i]>=0x30 && s[i]<=0x39){
        result=result*10+(s[i]-'0');
      }
    }
    s[pri]=result;
    pri++;
    //printf_tiny("%d\r\n",result);
  //}
  if(s[0]>0) { 
    while(1){
      if(pooli!=0){ // not line head
        while(pool[pooli]!=0x0){ pooli++; if(pooli==(80-1)) break;}
          // skip non zero, maybe string from last keyword
          
          // 
        pooli++;
      }
        
      // travel pool
      if(pool[pooli]!=0x0) { // not heading zero
        // skip any keyword
        if(pool[pooli+1] == 0x01){ pooli+=2; continue;} // PRINT  LL 01 AA .. AA 00
        if(pool[pooli+1] == 0x02){ pooli+=2; continue;} // RUN    LL 02 00
        if(pool[pooli+1] == 0x03){ pooli+=5; continue;} // FOR    LL 03 XX YY II AA .. AA 00
        if(pool[pooli+1] == 0x04){ pooli+=3; continue;} // NEXT   LL 04 @@ AA .. AA 00
        if(pool[pooli+1] == 0x05){ pooli+=4; continue;} // POKE   LL 05 AD DA 00
        if(pool[pooli+1] == 0x06){ pooli+=2; continue;} // LIST   LL 06 00
        if(pool[pooli+1] == 0x07){ pooli+=2; continue;} // DEBUG  LL 07 00
        if(pool[pooli+1] == 0x08){ pooli+=2; continue;} // NEW    LL 08 00
      }
      break; 
    }// while
  }  
  //printf_tiny("si=%d pi=%d\r\n",si,pri);
  //
  // line parsing
  //
  for(;si<40;si++){
  //
    // PRINT  LL 01 AA .. AA 00
    if(strncmp(&s[si],"PRINT",5)==0){ 
      s[pri]=0x01; si+=5;
      char start=0,end=0;
      for( i=si;i<LINE_LENGTH;i++){
        if(s[i]=='"'){
          if(start==0){start=i+1; continue;}
          if(end==0){end=i; i=LINE_LENGTH;}//break;}
        }
      }
      if(start>0 && end>0){
        if((end-start)>7){ end=start+7;}
        strncpy(&s[pri+1],&s[start],end-start);
        pri+=end-start+1;
      }
      s[pri]=0x0;
      break;
    }
    if(strncmp(&s[si],"RUN",3)==0){s[pri]=0x02; pri++; s[pri]=0x0; si+=3;break;}// RUN    LL 02 00
    // FOR    LL 03 XX YY II AA .. AA 00
    if(strncmp(&s[si],"FOR",3)==0){ // FOR I = 0 TO 255
      s[pri]=0x03; si+=3;
      char ii=si;      
      char start=0,end=0;
      start=strstr(&s[si],"=")-s;
      if(start==NULL) break;
      end=strstr(&s[si],"TO")-s;
      if(end==NULL) break;
      length=start-ii;
      from=s+ii;
      to=s+ii+strlen(&s[ii]); // find the tail
      *(s+start)=0x0; // let '=' become 0x0
      if(debug){printf_tiny("%s\r\n",from);}
      while(*from==0x20 && length>0){from++; length--; if(length==0)break; if(debug){printf_tiny("%s\r\n",from);}}
      if(debug){printf_tiny("%x\r\n",from[strlen(from)-1]);}
      while(from[strlen(from)-1]==0x20 && length>0){from[strlen(from)-1]=0x0; length--;if(length==0)break; }
      if(debug){printf_tiny("%x\r\n",length);}
      strncpy(to,from,length);
      
      result=0;
      for( i=start;i<end;i++){
        if(s[i]>=0x30 && s[i]<=0x39){
          result=result*10+(s[i]-'0');
        }        
      }
      s[pri+1]=result; // min
      result=0;
      for( i=end+2;i<LINE_LENGTH;i++){
        if(s[i]>=0x30 && s[i]<=0x39){
          result=result*10+(s[i]-'0');
        }        
      }
      s[pri+2]=result; // max
      s[pri+3]=0x0; // for loop variable
      ff[++ffi]=pooli+pri+3; // save the loop variable into fifo 
      pri+=4;
      strncpy(&s[pri],to,length);
      pri+=length;      
      s[pri]=0x0;
      break;
    }
    // NEXT   LL 04 @@ AA .. AA 00
    if(strncmp(&s[si],"NEXT",4)==0){
      s[pri]=0x04; si+=4;
      pri++;
      length=strlen(&s[si]);
      strncpy(&s[pri+1],&s[si],length); // variable string move right 1 byte
      s[pri+1+length]=0x0;
      if(debug){printf_tiny("%s\r\n",&s[pri+1]);}
      s[pri]=ff[ffi--];
      pri++; // pointer point to the string head
      // strip the ' '
      length=strlen(&s[pri]);
      from=&s[pri];
      to=&s[pri]; // find the tail
      if(debug){printf_tiny("%s\r\n",from);}
      while(*from==0x20 && length>0){from++; length--; if(length==0)break; if(debug){printf_tiny("%s\r\n",from);}}      
      if(debug){printf_tiny("%d\r\n",length);}
      if(debug){printf_tiny("%x\r\n",from[length-1]);}
      while(from[length-1]==0x20 && length>0){from[length-1]=0x0;length--; if(length==0)break; if(debug){printf_tiny("%s\r\n",from);}}      
      if(debug){printf_tiny("%x\r\n",length);}
      if(debug){printf_tiny("%x %x\r\n",(char)to,(char)from);}
      strncpy(to,from,length);
      to[length]=0x0;
      pri+=strlen(&s[pri]);
      break;
    }
    // POKE   LL AD DA 00
    if(strncmp(&s[si],"POKE",4)==0){
      s[pri]=0x05; si+=4;
      result=0;
      for( i=si;i<LINE_LENGTH;i++){
        if(s[i]>=0x30 && s[i]<=0x39){
          result=result*10+(s[i]-'0');
        }
        if(s[i]==','){s[pri+1]=result;result=0;continue;}
        if(s[i]==0x0){s[pri+2]=result;break;}
      }
      pri+=3;
      s[pri]=0x0;
      break;
    }
    if(strncmp(&s[si],"LIST",4)==0){s[pri]=0x06; pri++; s[pri]=0x0; si+=4;break;}
    if(strncmp(&s[si],"DEBUG",5)==0){s[pri]=0x07; pri++; s[pri]=0x0; si+=5;break;}
    if(strncmp(&s[si],"NEW",3)==0){s[pri]=0x08; pri++; s[pri]=0x0; si+=3;break;}
  }
  
   // if line number exist, insert new one into the pool
  if(s[0]>0) { 
       
      memcpy(&pool[pooli],s,pri); 
  }else{
    // intepreter: single run
    single_run(s); // skip line number field, because intepreter mode has no line number
  }

  if(debug){
    char memcnt=0;
    printf_tiny("debug:\r\n");
    for (char i=0;i<80;i++){
     
      printf_tiny("%x ",pool[i]);
     
      if((i+1)%16==0){printf_tiny("\r\n");}
    }
    printf_tiny("\r\n");
    
    printf_tiny("%d %d %d",ff[0],ff[1],ff[2]);

    printf_tiny("\r\n");
    for( i=0;i<LINE_LENGTH;i++){
      printf_tiny("%x ",s[i]);
    }
    printf_tiny("\r\n");
    for( i=0;i<LINE_LENGTH;i++){
      printf_tiny("%c ",s[i]);
    }
    printf_tiny("\r\n");
  }
  return 255;
}

void main(void)
{
  char ii=1;

  UART_Init(4800UL);
  /*
  for(int i=0;i<6;i++){
    P0=~P0;
    for(volatile int dly=0;dly<30000;dly++);
  }
  */
  printf_tiny("SP=%x\r\n",SP);    
    while(1)
    {
      char ch=getchar();
      if(ch == 0xd){
        line[ii]=0x0;
        ii=1;
        printf_tiny("\r\n");
        char err=process(line);
        //printf_tiny("%d\n",err);
        if(err != 255){
          for(char i=0;i<err;i++)
            printf_tiny(" ");
          printf_tiny("^\r\n");
        }
        ii=1;
        for(char i=0;i<LINE_LENGTH;i++) line[i]=0x0;
        /*
        while(1){
          char c=line[ii++];
          if(c==0x0) break;
          printf_tiny("%x ",c);
        }
        */
        printf_tiny("\r\n");
        ii=1;
        //printf_tiny("%s\r\n",line);
      }else{
        line[ii++] = ch;
        printf_tiny("%c",ch);
      }
      
    }
}