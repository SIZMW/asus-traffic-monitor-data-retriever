ASUS Router Traffic Monitor Data Retriever
=================================================

## Description
This program can be used to retrieve the daily traffic monitor data from an ASUS AC66U router.

For those who want to monitor or track their daily and monthly internet usage, whether it be to identify unfamiliar data use or track their usage against ISP data caps, this program provides a means to gather, summarize, and extract their router traffic data and allow them to further visualize it as they see fit.

Many routers with DD-WRT firmware offer the capability to see bandwidth usage, both live and in the past. Some provide basic views within the router administration web pages to see this information, but it isn't always easy to extract this and store it for further use. This program accesses the traffic monitor pages in the ASUS AC66U router administration, extracts the bandwidth usage data, and compiles and summarizes it in a Excel workbook that can then be used to generate charts and graphs for easy visualization.

#### References

* [dbrgn/asus-traffic-fetcher](https://github.com/dbrgn/asus-traffic-fetcher) was the initial inspiration to write this program, but with the added ability to export to Excel workbooks.

## Build
This program requires:

* [Python 2.7](https://www.python.org/download/releases/2.7/)
* [Selenium](https://pypi.python.org/pypi/selenium/2.7.0)
* [XlsxWriter](https://pypi.python.org/pypi/XlsxWriter)
* [Docopt](https://pypi.python.org/pypi/docopt)
* [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) for logging in and retrieving the data. Place the executable `chromedriver.exe` in the project folder.
* An ASUS router to connect to (tested with AC66U)

See the [requirements.txt](requirements.txt) for more information.

## Execution

#### Arguments
To retrieve and store the usage data in an Excel workbook, run the program as follows:
```
python retrieve_traffic_data.py -o "path/to/output/Excel/workbook.xlsx"
```

The arguments are:

* `output_file`: The output file where the daily usage and summary will be written.

ASUS routers resolve to using the `http://router.asus.com` address from within the network, so there is no need to provide the IP address of the router. If your router exists at a different IP, edit the `ROUTER_URL` value in the script.

You can run `python retrieve_traffic_data.py -h` for further help.

#### Output
An example of the daily usage output in the Excel workbook is shown below:

|     Date     | Download (GB) | Upload (GB) |  Total (GB)  |
|--------------|---------------|-------------|--------------|
|  2015-07-31  |      1.60     |     0.7     |     2.39     |
|  2015-08-01  |      2.90     |     0.4     |     3.30     |
|  2015-08-02  |      0.40     |     0.3     |     0.70     |
|  2015-08-03  |      1.25     |     0.9     |     2.10     |

An example of the monthly summary output in the Excel workbook is shown below:

| Year | Month | Download (GB) | Upload (GB) |  Total (GB)  |
|------|-------|---------------|-------------|--------------|
| 2015 |   7   |      1.60     |     0.7     |     2.30     |
| 2015 |   8   |      4.55     |     1.7     |     6.25     |
