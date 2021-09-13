# simple51ide
simple IDE for AT89S52
  
這是一個簡單風格的AT89S51/52專用整合開發環境

AT89S系列MCU是ATMEL公司開發的MCS-51族系單晶片  
可線上燒錄程式（ISP）是它的一大特點  
本計畫使用Arduino As ISP，讓Arduino作為AT89S單晶片的程式上傳器  
並且使用python程式建構一個整合開發環境（IDE）  
本IDE有以下特點：  
  
1.帶有c語言文法著色的文字編輯器  
2.搭配SDCC進行c語言編譯  
3.搭配修改過的ArduinoAsISP進行單晶片程式上傳  
4.修改過的ArduinoAsISP可作為串列埠中繼，將單晶片的串列埠資料傳送到電腦  
5.內建串列埠監視視窗，可顯示來自單晶片的串列埠資料  
6.（計畫中）內建串列埠資料繪圖器，將串列埠資料即時繪製圖形  

程式上傳器（ArduinoAsISP）運作原理圖  
[](./test.jpg)  
