# CircuitPython Console Uploader
A simple Python script that allows you to upload files to your CircuitPython device's REPL.
Requires Python 3.6 or higher and PySerial.

## Usage
```cpcupload -p [port] -f [files]```

Options:
* -p, --port: The port your CircuitPython device is connected to. Required.
* -f, --files: The files you want to upload. Required.
* -t, --to-dir: The directory you want to upload the files to. Optional. Defaults to the root directory.