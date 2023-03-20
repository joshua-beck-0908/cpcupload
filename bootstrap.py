import time
import supervisor
import sys
import microcontroller
import traceback
import os
import math

class _Bootstrap:
    def __init__(self):
        self.blockSize = 64
        self.buffer = bytearray(self.blockSize)

    def dataReady(self):
        return supervisor.runtime.serial_bytes_available

    def readBlock(self, file, limit):
        cmd = sys.stdin.read(2).strip()
        if cmd != 'b':
            print('ERR')
            print(cmd.encode())
            raise ValueError(f'Got {cmd} instead of block start.')
        else:
            print('RDY')
        sys.stdin.readinto(self.buffer)
        file.write(bytes(self.buffer[0:limit]).replace(b'\x053', b'\x03').replace(b'\x05d', b'\x0d').replace(b'\x055', b'\x05'))
        print('OK')

    def readfile(self, filename):
        partialBlock = 0
        file = open(filename, 'wb')
        fileSize = int(input())
        partialBlock = fileSize % self.blockSize
        blockCount = math.ceil(fileSize / self.blockSize)
        for i in range(blockCount):
            if i == blockCount - 1 and partialBlock > 0:
                self.readBlock(file, partialBlock)
            else:
                self.readBlock(file, self.blockSize)
        file.close()

    def setdir(self, dirname):
        try:
            os.stat(dirname)
        except OSError as e:
            os.mkdir(dirname)
        os.chdir(dirname)
                

    def run(self):
        while not self.dataReady():
            time.sleep(0.1)

        self.data = ''
        while True:
            filename = input()
            if filename == '-':
                break
            elif filename == '':
                continue
            elif filename.startswith('@dir'):
                self.setdir(filename.split(':')[1])
                continue
            self.readfile(filename)
        microcontroller.reset()

try:
    boot = _Bootstrap()
    boot.run()
except Exception as exc:
    print(traceback.format_exception(exc)[0])
    while True:
        pass
    
    
