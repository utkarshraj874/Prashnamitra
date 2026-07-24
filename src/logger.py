import logging #python ki built in module ahi 
from pathlib import Path 
#hum log ka use  karte ataki kahi pe bhi kissi bhi file ya processs me error aaye
# to direct pata chal jaye , sirf error likha hua na aaya , balki exact error kya hai wo pta chal jaye

LOG_DIR =  Path("logs")# log ek dairy type ka hai jo records rakhta bahia ,, kab kaya ho raha ahi 

LOG_DIR.mkdir(exist_ok=True)#Create folder  Agar already hai to error mat do.

LOG_FILE = LOG_DIR/"app.log"# app.log file banegi 
#logs folder hum banate hain.
#👉 app.log logging library khud bana deti hai jab pehla log likha jata hai

logging.basicConfig(
    filename=LOG_FILE,#log ko errminal me save nhi karni hai 
    level=logging.INFO,#info aur  usse uper waale  logs hi record karo 
    format = "%(asctime)s | %(levelname)s | %(message)s| %(filename)s ",
    #log file ka format kaisa hoga eg;- 2026-07-22 11:20:32 ,INFO ,PDF Loaded
)#logging bhi ek type ka settitng hai jiase m]phone me date time , language set karte ahi 
#

logger = logging.getLogger("DocuMind")
#python me log ke alag alg level hai , 1.debug, 2.info, 3.warning, 4.error, 5.critical
#debug:- program ke ander kya ho rha ahi , 2. info:- sab norrmal chl rha ahi eg:-PDF Loaded Embeddings Created ,Chat Started
# warning :- program chl raha hai lekin kuch unsual hai , 4 error :- pragram ka ek part fail ho gya  
#critical :- program almost crash 
