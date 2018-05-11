# ezlogparse
Parser for data logs saved by ezproxy using Python.

## Usage / command:
> $ python ezlogparse.py --argument value

| Arguments | Description | Default Values | Type |
| --- | --- | --- | --- |
| --version | Prints version | False | None
| --verbose, -v | Verbose output, prints statistics | False | None
| --dir, -d | Directory of log files | pwd* | str
| --ext, -e | Extension of files | *.log | str
| --in_file, -f | Use custom input log file | data.log | string
| --out_file, -o | Specify output file | parsed.csv | string
| --stat_file, -s | Specify output stat file | stat.csv | string
| --keyword, -k | Lookup filtering keyword | '.pdf' | string
| --timewindow, -t | Specify timewindow | 14400 seconds | integer
| --oncampaddr, -ipc | Specify campus ip address | 10.X.X.X | string

*present working directory

Notes:

- Directory is the current working directory. If this is unspecified, then the parser will only analyze one default/specified log.
- Need to specify '*' if we want to run the script on all the files with that file extension. Note that if you want to run multiple files, the script only works by opening a separate directory from the current working directory of the script.
    
Sample usage: 

> $ python ezlogparse.py -v -f ezproxy.log -gst

### Version:

Version 2.0:
  - Able to generate statistical data

Version 1.0:
  - Parser working with csv output
  
### To implement:

- Get actual content name based on HTTP requests
