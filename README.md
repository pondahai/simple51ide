# simple51ide
simple IDE for AT89S52  
## 前言  
這是一個簡單風格的AT89S51/52專用整合開發環境  
![](202109131752.png)  
AT89S系列MCU是ATMEL公司開發的MCS-51族系單晶片  
可線上燒錄程式（ISP）是它的一大特點  
本計畫使用Arduino As ISP，讓Arduino作為AT89S單晶片的程式上傳器  
並且使用python程式建構一個整合開發環境（IDE）  
這個IDE的規劃理念是：讓第一個範例程式以最快時間上傳運作  
因此讓過程中的設定步驟以預設值的方式存在  
以期待對使用者的干擾降到最低  
  
## 功能    
  
1.帶有c語言文法著色的文字編輯器  
2.搭配SDCC進行c語言編譯  
3.搭配電腦端的avrdude以及arduino修改過的ArduinoAsISP進行單晶片程式上傳  
4.修改過的ArduinoAsISP可作為串列埠中繼，將單晶片的串列埠資料傳送到電腦  
5.內建串列埠監視視窗，可顯示來自單晶片的串列埠資料  
6.（計畫中）內建串列埠資料繪圖器，將串列埠資料即時繪製圖形  

## 限制  
* 僅能使用ATMEL 89S 系列之 8051 核心 MCU. 
* 程式上傳器要用Arduino Leonardo系列（32u4核心）  
  才能自動切換上傳模式與串列埠中繼模式  
  如要用其他核心的Arduino則需要改ArduinoAsISP.ino  
  另外設計外部開關切換  
  或是用開機後延時的方式切換  
  RESET時先進入上傳模式  
  等超時後再切換成串列埠中繼模式  
  然後每次要上傳前手動RESET Arduino  

## 原理  
### 程式上傳器  
程式上傳器（ArduinoAsISP）運作原理圖  
![](arduinoAs51ISP.png) 
我放在  
/ArduinoISPserialThrough  
這個ArduinoAsISP有修改過  
可以讓ArduinoAsISP除了原本的程式上傳功能外  
還可以自動切換成串列埠資料中繼站  
注意！！  
這裡的ArduinoAsISP一定要使用核心為32u4的Arduino  
程式上傳器的接線圖    
![](ISP.png) 
因為89S系列跟AVR系列（arduino用）都是ATMEL出的MCU  
他們的ISP協定是相同的  
差別是acrdude程式需要在原avrdude.conf中加入89S52的設定  
這樣avrdude才能上傳程式給89S系列  
  
### 整合開發環境（IDE）  
IDE本身使用python語言開發  
整體使用tk圖形化介面為架構  
搭配外部工具 c語言編譯器SDCC 以及 AVR上傳程式avrdude  

### 使用方法  
目前還在開發階段  
主程式 simple51ide.py  
須自行處理程式庫相依性問題  
sdcc與avrdude也要另行下載安裝  
程式下載器必須使用32u4核心的arduino  
89S52的串列輸出入可以透過arduino中繼給電腦端  
電腦端使用終端機程式就可以與89S52互動  
89S52最基本可運作的組態如下電路圖所示  
![](SCH.png) 
  
## 注意事項  
僅能使用ATMEL 89S 系列之 8051 MCU  
相關操作需有經驗方可為之，惟風險自負  
