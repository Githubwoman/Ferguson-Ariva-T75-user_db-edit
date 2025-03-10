#import binascii
#import crcmod
from crc import Calculator, Crc32
from sys import argv
import mmap

#size = 26416
offset = 64
#crcfunc = crcmod.predefined.mkPredefinedCrcFun('crc-32-bzip2')
calculator = Calculator(Crc32.BZIP2, optimized=True)
with open(argv[1], "r+b") as fh:
    with mmap.mmap(fh.fileno(),0) as mm:
        CRC32_db = mm[48] + (mm[49] << 8) + (mm[50] << 16) + (mm[51] << 24)
        print("CRC from file %s = %s%s%s%s" % (argv[1],hex(mm[51]).lstrip("0x"),hex(mm[50]).lstrip("0x"),hex(mm[49]).lstrip("0x"),hex(mm[48]).lstrip("0x")))
        print(hex(CRC32_db).lstrip("0x"))
        CRC32 = calculator.checksum(mm[offset:]) & 0xffffffff
#        CRC32 = ccrcfunc(mm[offset:s]) & 0xffffffff
#        print(hex(CRC32))
        invCRC32 = 0xffffffff - CRC32
        print("MATCH!!!!") if (invCRC32 == CRC32_db) else print("BAD CRC32!!!!")

#        print("CRC32-bzip2: %s" % hex(CRC32).lstrip("0x"))
        print("CRC32-bzip2 inv: %s" % hex(invCRC32).lstrip("0x"))

#        with open("user_db_mod.bin", "w+b") as fw:
#            fw.write(mm)

