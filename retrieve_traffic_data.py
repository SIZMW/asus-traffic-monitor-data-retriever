"""
retrieve_traffic_data.py

Retrieve the daily traffic data from an ASUS AC66U router and write the data and a summary into an Excel workbook.
Router login is requested at the start of the program.

Usage:
    retrieve_traffic_data.py -o <output_file>
    retrieve_traffic_data.py -h | --help
    retrieve_traffic_data.py -v | --version

Options:
    -h --help           Show this help information.
    -v --version        Show version number.
    -i <ip>             The router IP address.
    -o <output_file>    The output Excel workbook.
"""

from __future__ import print_function
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC

import csv
import docopt
import getpass
import xlsxwriter

ROUTER_URL = 'http://router.asus.com/'
TRAFFIC_PAGE = 'Main_TrafficMonitor_daily.asp'
LOGIN_PAGE = 'Main_Login.asp'
CHROME_DRIVER_FILE = 'chromedriver.exe'

DATE_COL = 'Date'
DOWNLOAD_COL = 'Download'
UPLOAD_COL = 'Upload'
TOTAL_COL = 'Total'
YEAR_COL = 'Year'
MONTH_COL = 'Month'

"""
The DateTraffic class defines an entry in the traffic log for data usage on a specific day.
"""
class DateTraffic(object):
    """
    Constructs a DateTraffic instance.

    Arguments:
        dt: The date of the entry.
        dl: The download usage.
        ul: The upload usage.
    """
    def __init__(self, dt, dl, ul):
        self.date = dt
        self.dl = dl
        self.ul = ul

    """
    Returns the total usage for this day.

    Returns:
        A float
    """
    @property
    def total(self):
        return self.dl + self.ul

    """
    Returns the string representation of this object.

    Returns:
        A string
    """
    def __repr__(self):
        return '(date=%s, dl=%s, ul=%s, total=%s)' % (self.date, self.dl, self.ul, self.total)            

"""
Retrieves the daily usage data from the traffic monitor page in the ASUS router management web page.

Arguments:
    username: The user name for the administrator login.
    password: The password for the administrator login.

Returns:
    An array of all the daily traffic usage entries.
"""
def retrieve_router_data(username, password):
    # Set driver properties
    capabilities = DesiredCapabilities.CHROME
    capabilities['loggingPrefs'] = {'browser':'ALL'}
    driver = webdriver.Chrome(CHROME_DRIVER_FILE, desired_capabilities=capabilities)
    wait = WebDriverWait(driver, 120)
    driver.implicitly_wait(2)
    
    # Log in the router
    driver.get(ROUTER_URL + LOGIN_PAGE)
    wait.until(EC.element_to_be_clickable((By.NAME,'login_username')))
    driver.find_element_by_name('login_username').click()
    driver.find_element_by_name('login_username').send_keys(username)
    driver.find_element_by_name('login_passwd').click()
    driver.find_element_by_name('login_passwd').send_keys(password)
    driver.find_element_by_css_selector('.button').click()
    driver.implicitly_wait(2)

    # Go to traffic page
    driver.get(ROUTER_URL + TRAFFIC_PAGE)
    driver.implicitly_wait(1)

    # Get daily data
    baseTable = driver.find_element_by_css_selector('.FormTable_NWM')
    odd_table_rows = baseTable.find_elements_by_class_name('odd')
    even_table_rows = baseTable.find_elements_by_class_name('even')

    all_rows = []
    all_rows.extend(odd_table_rows)
    all_rows.extend(even_table_rows)

    print('Pulled router daily traffic data.')
    date_traffics = []

    # Parse table rows
    for row in all_rows:
        items = row.find_elements_by_tag_name('td')

        date = items[0].text
        dl = float(items[1].text.split(' ')[0])
        ul = float(items[2].text.split(' ')[0])

        date_traffics.append(DateTraffic(date, dl, ul))

    # Sort data
    date_traffics.sort(key=lambda x: x.date, reverse=False)
    driver.quit()

    print('Sorted traffic table data.')
    return date_traffics

"""
Writes the daily traffic usage entries and a summary into Excel worksheets.

Arguments:
    date_traffics: The array of all the daily traffic usage entries.
    output_file: The output Excel workbook to write the data into.
"""
def write_workbook_output(date_traffics, output_file):
    # Write daily data into Excel sheet
    workbook = xlsxwriter.Workbook(output_file)
    usage_wkst = workbook.add_worksheet('Router Usage')
    usage_wkst.set_column(0, 3, 11)
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

    row = 1
    col = 0
    for dt in date_traffics:
        usage_wkst.write_datetime(row, col, format_date(dt.date), date_format)
        usage_wkst.write_number(row, col + 1, dt.dl)
        usage_wkst.write_number(row, col + 2, dt.ul)
        usage_wkst.write_number(row, col + 3, dt.total)
        row = row + 1

    # Create table in worksheet
    usage_wkst.add_table('A1:D{0}'.format(str(len(date_traffics) + 1)), {
        'header_row': True,
        'columns': [{
            'header': DATE_COL
        }, {
            'header': DOWNLOAD_COL
        }, {
            'header': UPLOAD_COL
        }, {
            'header': TOTAL_COL
        }] 
    })

    # Create dictionary of year and month entries
    dt_summary = dict()    
    for dt in date_traffics:
        dt_datetime = format_date(dt.date)

        dt_year = dt_datetime.year
        dt_month = dt_datetime.month

        dt_key = '{0}-{1}'.format(dt_year, dt_month)

        if(dt_key in dt_summary):
            dt_summary[dt_key][DOWNLOAD_COL] += dt.dl
            dt_summary[dt_key][UPLOAD_COL] += dt.ul
            dt_summary[dt_key][TOTAL_COL] += dt.total
        else:
            dt_summary[dt_key] = {
                DOWNLOAD_COL: dt.dl,
                UPLOAD_COL: dt.ul,
                TOTAL_COL: dt.total
            }

    summ_wkst = workbook.add_worksheet('Router Summary')
    summ_wkst.set_column(0, 4, 11)

    # Write monthly summary data into Excel sheet
    row = 1
    col = 0
    for dts in sorted(dt_summary.keys()):
        dt_year = int(dts.split('-')[0])
        dt_month = int(dts.split('-')[1])

        summ_wkst.write_number(row, col, dt_year)
        summ_wkst.write_number(row, col + 1, dt_month)

        summ_wkst.write_number(row, col + 2, dt_summary[dts][DOWNLOAD_COL])
        summ_wkst.write_number(row, col + 3, dt_summary[dts][UPLOAD_COL])
        summ_wkst.write_number(row, col + 4, dt_summary[dts][TOTAL_COL])
        row = row + 1

    # Create table in worksheet
    summ_wkst.add_table('A1:E{0}'.format(str(len(dt_summary.keys()) + 1)), {
        'header_row': True,
        'columns': [{
            'header': YEAR_COL
        }, {
            'header': MONTH_COL
        }, {
            'header': DOWNLOAD_COL
        }, {
            'header': UPLOAD_COL
        }, {
            'header': TOTAL_COL
        }] 
    })

    workbook.close()

"""
Returns the datetime object representation of the date string.

Arguments:
    date_str: The string form of the date (yyyy-mm-dd)

Returns:
    A datetime object
"""
def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='retrieve_traffic_data.py 0.1')
    output_file = arguments['-o']
    username = getpass.getpass('User Name: ')
    password = getpass.getpass('Password: ')

    write_workbook_output(retrieve_router_data(username, password), output_file)
    print('Updated Excel workbook.')
