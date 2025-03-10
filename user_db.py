import binascii
import mmap
from sys import argv, exit
from os.path import exists
from crc import Calculator, Crc32

# Reading a binary file in chunks
size = 192  # Define the chunk size
Channel_name = ""
Channels = {}  # {NP : [SID, LCN, Channel_name, offset]}
Channels_LCN = {}  # {LCN : [NP, SID, Channel_name, offset]}
New_Channels = {}

def channel_list_print(Channels_data):
    for i in range (1,199):
        try:
            Channel = Channels_data[i]
            SID = Channel[0]
            LCN = Channel[1]
            NP = i
            CH_Name = Channel[2]
            print("NP: %2i - SID: %2i, LCN: %2i, Name: %s" % (i, SID, LCN, CH_Name))
        except:
#            print("No channel number: %2i" % i)
            continue


f = open(argv[1], 'r+b')
try:
    header = f.read(476)
    offset = 476
    while True:
        print("---------------------------------- MUX ----------------------------------")
        print("MUX offset = %i" % offset)
        chunk = f.read(8)
        offset += 8
        chunk = f.read(8)
        offset += 8
        if not chunk:
            print("Offset: " + str(offset))
            print(chunk)
            break
        for i in range(0,int(chunk[0])):  # number of channels in MUX
            chunk = f.read(size)
            if chunk[0] != 81: # Not a new TV channel data
                print("Offset: " + str(offset))
                print(chunk)
                break
            for x in range(140,192):
                if chunk[x] != 0 and chunk[x] != 1:  # removing zeroes from channel name string
                    Channel_name += chr(chunk[x])
            SID = int(chunk[14])         # offset 14 from begining of Channel record contain its SID
            CH_number = int(chunk[20]+1) # offset 20 from begining of Channel record contain its CH number
            LCN = int(chunk[26])         # offset 20 from begining of Channel record contain its LCN
            Channels[CH_number] = [SID, LCN, Channel_name, offset]
            Channels_LCN[LCN] = [CH_number, SID, Channel_name, offset]
            print("Channel name: %s ; SID: %i ; Number: %i" % (Channel_name, SID, CH_number))
            Channel_name = ""
#            print(binascii.hexlify(chunk[:92]))
            offset += size
            chunk = f.read(4) # last 4 bytes from channel data
            offset += 4

        # Search for MUX definition end pattern: E0 3F
        pattern = b'\xE0\x3F'
        print("Offset = %i" % offset)
        with open(argv[1], "r+b") as fh:
            with mmap.mmap(fh.fileno(), offset + 512) as mm:
               pos = offset
               while -1 != (pos := mm.find(pattern, pos + 1)):
                   print(pos)
                   break
        if pos != -1:
            chunk = f.read(pos-offset)
            offset = pos
            chunk = f.read(2) # read MUX data end.
            offset += 2
        if chunk[0] != 224: # xE0
#            print("Error offset = %i" % offset)
#            print(binascii.hexlify(chunk))
            print("No MUX data end")
            break
 
        # Process the chunk (for demonstration, we'll print it)
#        hex_data = map(hex, chunk)
#        print((hex_data))
except:
    print("Problem when reading %s file!!!" % argv[1])

print("\nActual channel list by channel number:")
channel_list_print(Channels)

#Check if one need new LCN.txt file
LCN_file_created = False
if (not exists("LCNs.txt")):
    print("\nCreating LCN.txt file from actual channel list")
    LCN_file_created = True
    f_lcn = open("LCNs.txt", 'w+')
    for i in range (1,99):
        try:
            Channel = Channels[i] # {NP : [SID, LCN, Channel_name, offset]}
            LCN = Channel[1]
            NP = i
#            print("NP: %2i - LCN: %2i" % (NP, LCN))
            f_lcn.write("%s:%s\n" % (NP, LCN))
        except:
#            print("No channel number: %2i" % i)
            continue
    f_lcn.close()

if (LCN_file_created):
    exit(0)

# read LCN.txt file line by line
f_lcn = open("LCNs.txt", 'r')
line = '\0'
try:
    print("\nFile LCNs.txt (channel number:LCN) found!")
    while True:
        line = f_lcn.readline()
        [NP, LCN] = line.split(":", 1)
        if int(LCN) in Channels_LCN.keys():
#            print("LCN %s" % LCN)
            Channel_LCN = Channels_LCN[int(LCN)] # {LCN : [NP, SID, Channel_name, offset]}
            NP_old = Channel_LCN[0]
            Channel = Channels[NP_old]
            Channel_LCN[0] = NP  # new NP for channel
            New_Channels[int(NP)] = Channel
        else:
            print("Unknown LCN: %s" % int(LCN))
except:
    print("Can't read LCNs.txt file (channel number:LCN) !!!") if (line == '\0') else print("End of LCN.txt file.")
finally:
    f_lcn.close()

# Copy channels which wasn't in LCNs.txt file
for i in range (1,99):
    try:
        NP = i
        if NP in Channels.keys():
            Channel_old = Channels[i] # {NP : [SID, LCN, Channel_name, offset]}
            LCN_old = Channel_old[1]
            Channel_LCN = Channels_LCN[LCN_old] # {LCN : [NP, SID, Channel_name, offset]}
            if (NP == Channel_LCN[0]):  # If this channel number wasn't changed
                if NP in New_Channels.keys(): # but there is new channel on that positon then there is a problem.
                    print("Channel with %s LCN hasn't change position but new channel set on it!!!!" % LCN_old)
                    New_Channels[NP+100] = Channels[NP]
                else: # otherwise there is a need to copy that channel to new list.
                    New_Channels[NP] = Channel_old
                    print("Copying old channel number %s to new list." % NP)
        print("NP: %2i - LCN: %2i" % (NP, LCN))
    except:
#        print("No channel number: %2i" % i)
        continue

print("\nNew channel list by channel number:")
channel_list_print(New_Channels)

#Ask user to proceed further
val = "0"
while (val != "Y" and val != "N"):
    val = input("\nDo you want to proceed and create new 'user_db_mod.bin' file? (Y/N): ")
#    print(binascii.hexlify(bytes(val,'utf-8')))

if val == "N":
    f.close()
    exit(1)

# Proceed to create modified user_db.bin file
mm = mmap.mmap(f.fileno(), 0)
for i in range (1,199):
    try:
        NP = i
        if NP in New_Channels.keys():
            Channel_new = New_Channels[i] # {NP : [SID, LCN, Channel_name, offset]}
            offset = Channel_new[3]
            mm[offset+20] = NP - 1 # user_db.bin contain channel numbered from 0
#            print("Found channel NP data: %2i " % (NP))
    except:
#        print("No channel number: %2i" % i)
        continue

# Calculate CRC32 with bzip2 and inverted output
calculator = Calculator(Crc32.BZIP2, optimized=True)
CRC32 = calculator.checksum(mm[64:]) & 0xffffffff
invCRC32 = 0xffffffff - CRC32
print("Calculated CRC for 'user_db_mod.bin': %s " % hex(invCRC32).lstrip("0x"))

# little-endian encoding
mm[48] = invCRC32 & 0xff # LSB
mm[49] = (invCRC32 & 0xff00) >> 8
mm[50] = (invCRC32 & 0xff0000) >> 16
mm[51] = (invCRC32 & 0xff000000) >> 24 # MSB
#print(binascii.hexlify(mm[48:52]))

# Creat new user_db_mod.bin file:
try:
    f_out = open("user_db_mod.bin", "w+b")
    f_out.write(mm)
    f_out.close()
    print("\nCreated 'usr_db_mod.bin' file.")
except:
    print("\nError creating 'usr_db_mod.bin' file!!!!!")
finally:
    mm.close()
    f.seek(0)
    f.close()

# CRC32(hex) = 76 BE 9E 57

# E0 3F -- MUX data end?
# 51 80 - channel data start
# 8 bytes before first channel data start on a MUX there is a number of channels on that MUX.
