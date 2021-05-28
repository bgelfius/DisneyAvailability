import json 
from datetime import datetime
from datetime import date
from dateutil import parser
import datetime
from markupsafe import escape
from DisneyScraper import ClickType
from DisneyScraper import Park
from DisneyScraper import DisneyScraper 
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import Flask
app = Flask(__name__)


import debugpy
debugpy.debug_this_thread()

#@app.route('/Initialize')
#def ByDate(passtype, sdate = date.today(), edate = None):


@app.route('/ByDate/<passtype>/<sdate>')
@app.route('/ByDate/<passtype>/<sdate>/<edate>')
def ByDate(passtype, sdate = date.today(), edate = None):
    f = DisneyScraper()

    
    if (escape(passtype) == 'ThemePark'):
        page = f.manipulatePage(ClickType.ThemePark)
    elif (escape(passtype) == 'Resort'):
        page = f.manipulatePage(ClickType.Resort)
    elif (escape(passtype) == 'Annual'):
        page = f.manipulatePage(ClickType.Annual)
    else:
        raise ValueError

    startDate = datetime.datetime.strptime(escape(sdate), "%m-%d-%Y").date()
    if (edate == None):
        rc = f.checkByDate(startDate)
    else:
        endDate = datetime.datetime.strptime(escape(edate), "%m-%d-%Y").date()
        rc = f.getByDateRange(startDate, endDate)
    
    #print(rc))
    return json.dumps(rc, indent=4, sort_keys=True, default=str)

@app.route('/NextDate/<passtype>/<tpark>')
def NextDate(passtype, tpark ):
    f = DisneyScraper()
    
    if (escape(passtype) == 'ThemePark'):
        page = f.manipulatePage(ClickType.ThemePark)
    elif (escape(passtype) == 'Resort'):
        page = f.manipulatePage(ClickType.Resort)
    elif (escape(passtype) == 'Annual'):
        page = f.manipulatePage(ClickType.Annual)
    else:
        raise ValueError
    
    themepark = Park.MagicKingdom # default

    if (escape(tpark) == 'MagicKingdom'):
        themepark = Park.MagicKingdom
    elif(escape(tpark) == 'AnimalKingdom'):
        themepark = Park.AnimalKingdom
    elif(escape(tpark) == 'Epcot'):
        themepark = Park.Epcot
    elif(escape(tpark) == 'HollywoodStudios'):
        themepark = Park.HollywoodStudios
    else:
        raise ValueError
    
    rc = f.nextAvailableByPark(themepark)
    #print(rc))
    return json.dumps(rc, indent=4, sort_keys=True, default=str)
    
 
@app.route('/')
def Index():
    print("index")
    return ("hello Disney")





    