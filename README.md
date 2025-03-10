# Ferguson-Ariva-T75-user_db-edit
Python script to modify user_db.bin file from Ferguson Ariva T75 DVB-T decoder and change TV channels numbers.
## Required python libraries
Only one external: crc<br>
One can obtain it by using pip tool
```sh
pip install crc
```
### How to get user_db.bin file
1. Inset Pendrive into one of From Ferguson Ariva T75 decoder USB ports. If it is readable by decoder it will display message about USB Storage connection
2. Use remote control and press Menu then choose System and finally "Upgrade from USB". There choose to make "USB Copy" and confirm writing to USB storage.
### How to create LCNs.txt
LCNs.txt file contains pares of channel numbers and LCNs separated by colon each in a new line (NP:LCN). Where NP is channel number and LCN is sugested TV channel number provided by DVB-T broadcasting network.<br>
These data pairs will be used to change channels numbers contained in user_db.bin file.<br>
One can use user_db.py script to create initial LCNs.txt file. After first use of that script it will generate that file from user_db.bin file provided. It will be exactly same channels numbers as set in decoder.
### How to use user_db.py script
Script gets only one parameter which is name of the file to use as source. Mostly it will be: user_db.bin<br>
Example usage:<br>
```python
python user_db.py user_db.bin
```
### How to use user_db CRC32.py
That script can verify if CRC contained in user_db.bin file is correct.<br>
Example usage:<br>
```python
python user_db CRC32.py user_db.bin
```
