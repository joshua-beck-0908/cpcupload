#!/usr/bin/python3
import serial
import time
import re
import sys
import argparse
import os
import pyperclip
from traceback import format_exception
import math

filenameHelp = 'One or more filenames to upload.'
portHelp = 'The COM port name or device file.'
parser = argparse.ArgumentParser()
parser.add_argument('--files', '-f', help=filenameHelp, nargs='+')
parser.add_argument('--port', '-p', help=portHelp, required=True)
parser.add_argument('--to-dir', '-t')
args = parser.parse_args()
scriptDir = os.path.dirname(os.path.realpath(__file__))
blockSize = 64

cp = serial.Serial(args.port, 115200)

def sendBootstrap():
    cp.reset_input_buffer()
    cp.write(b'\x03\x02\x03\x03')
    time.sleep(0.3)
    cp.write(b'\r\r')
    time.sleep(0.2)
    if not cp.read_all().endswith(b'>>> '):
        raise RuntimeError('Board not responding.')
    cp.write(b'\x01')
    time.sleep(0.2)
    if not cp.read_all().endswith(b'raw REPL; CTRL-B to exit\r\n>'):
        raise RuntimeError('Board did not enter paste mode.')
    cp.write(b'\x05A\x01')
    response = cp.read(2)
    if response != b'R\x01':
        raise RuntimeError('Board does not support Raw REPL mode.')
    windowInterval = int.from_bytes(cp.read(2), byteorder='little', signed=False)
    window = windowInterval

    bootFile = open(os.path.join(scriptDir, 'bootstrap.py'), 'rb')
    while True:
        while window == 0 or cp.in_waiting > 0:
            cmd = cp.read(1)
            if cmd == b'\x01':
                window += windowInterval
            elif cmd == b'\x04':
                raise RuntimeError('Bootstrap too large for device.')
        data = bootFile.read(window)
        if data == b'':
            break
        cp.write(data)
        cp.flush()
        window = 0
    bootFile.close()
    cp.write(b'\x04')
    cp.read_until(b'\x04')

def reload():
    cp.write(b'\x04')
    time.sleep(0.5)

def send(inText):
    cp.write((inText.replace('\r', '').replace('\n', '\r') + '\r').encode())

def read():
    try:
        return cp.read_all().decode().replace('\r', '')
    except UnicodeDecodeError as e:
        raise ValueError(f'Read encountered raw data.\n{format_exception(e)}')

def readline():
    return cp.readline().decode().strip()

def expect(expectedResponse):
    response = readline()
    if response != expectedResponse:
        time.sleep(1) # debug
        print(cp.read_all()) # debug
        raise ValueError(f'Expected "{expectedResponse}" got "{response}"')

def cmd(data):
    print(f'> {data}')
    cp.flush()
    cp.reset_input_buffer()
    send(data)
    expect(data)

def getIndent(text):
    return int((len(text) - len(text.lstrip())) / 4)
  
def sendFile(filename):    
    shortName = os.path.basename(os.path.realpath(filename))
    print(f'Transmitting file:{filename}...')
    cmd(shortName)
    with open(filename, 'rb') as f:
        data = f.read()
    data = data.replace(b'\x05', b'\x055').replace(b'\x03', b'\x053').replace(b'\r', b'\x05d')
    cmd(str(len(data)))
    
    offset = 0
    for i in range(math.ceil(len(data) / blockSize)):
        #print(f'Block {i}')
        send('b')
        expect('RDY')
        block = data[offset:offset+blockSize]
        if len(block) < blockSize:
            block += b'\0' * (blockSize - len(block))
        cp.write(block)
        offset += blockSize
        expect('OK')

def sendDir(path):
    cp.reset_input_buffer()
    cmd(f'@dir:{os.path.basename(path)}')
    for fn in os.listdir(path):
        fn = os.path.join(path, fn)
        if os.path.isdir(fn):
            sendDir(fn)
        else:
            sendFile(fn)
    cmd(f'@dir:..')

def copyData():
    time.sleep(1)
    cp.flush()
    pyperclip.copy(cp.read_all().decode().replace('\r', ''))

def endTransmission():
    send('-')

    print('> -')
    time.sleep(0.2)
    
print('Transmitting bootstrap...')
sendBootstrap()
time.sleep(0.3)
if args.to_dir:
    cmd(f'@dir:{args.to_dir}')
fileList = []
for path in args.files:
    if os.path.isdir(path):
        fileList += [os.path.join(path, fn) for fn in os.listdir(path)]
    else:
        fileList.append(path)
        
for fn in fileList:
    if os.path.isdir(fn):
        sendDir(fn)
    #elif fn.lower().endswith('.zip'):
    #    sendZip(fn)
    else:
        sendFile(fn)
print('Resetting...')
endTransmission()
print('Done.')
