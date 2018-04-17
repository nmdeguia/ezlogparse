# ezlogparse
Parser for data logs saved by ezproxy using Python.

## Usage / command:
> $ python ezlogparse.py --argument value

| Arguments | Description | Default Values | Type |
| --- | --- | --- | --- |
| --verbose, -v | Verbose output, prints statistics | OFF | None
| --genstat, -gst | Generate statistical report | OFF | None
| --in_file, -f | Use custom input log file | data.log | string
| --out_file, -o | Specify output file | parsed.csv | string
| --stat_file, -s | Specify output stat file | stat.csv | string
| --keyword, -k | Lookup filtering keyword | '.pdf' | string
| --timewindow, -t | Specify timewindow | 14400 seconds | integer
| --oncampaddr, -ipc | Specify campus ip address | 10.X.X.X | string

Sample usage: 

> $ python ezlogparse.py -v -f ezproxy.log -gst

### Version:

Version 2.0:
  - Able to generate statistical data

Version 1.0:
  - Parser working with csv output
  
### To implement:

- Get actual content name based on HTTP requests
