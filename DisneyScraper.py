import enum
from datetime import datetime
from dateutil import parser
import datetime
from datetime import date, timedelta 
from dateutil import relativedelta
from dateutil import rrule
import time
import lxml
from lxml import html
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import re
import json 
#import calendar
from markupsafe import escape
from flask import Flask
app = Flask(__name__)



class ClickType(enum.Enum):
    ThemePark = 1
    Resort = 2
    Annual = 3
    NextMonth = 4
    PrevMonth = 5
    Day = 6

class Park(enum.Enum):
    MagicKingdom = 1
    AnimalKingdom = 2
    Epcot = 3
    HollywoodStudios = 4
 
class DisneyScraper:  
    _headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Pragma': 'no-cache',
        'Referrer': 'https://google.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    disneyURL = "https://disneyworld.disney.go.com/availability-calendar/?segments=tickets,resort,passholder&defaultSegment=passholders"
    _chromedriver = r'C:\ChromeDriver\chromedriver.exe'
   # _chromedriver = r'/usr/bin/chromedriver'
    _currentDate = date.today()
    _browser = None

    def __init__(self) -> None:
        options = Options()
        options.add_argument("--no-sandbox") #bypass OS security model
        options.add_argument("--disable-dev-shm-usage") #overcome limited resource problems
        options.add_argument("--headless")
        self._browser = webdriver.Chrome(executable_path=self._chromedriver, options=options)
        #self._browser.implicitly_wait(10)
        self._browser.get(self.disneyURL) 

    def __del__(self):
        self._browser.close()
              
    def manipulatePage(self,  click : ClickType , day : int  = 1):
        
        time.sleep(5)

        if click == ClickType.ThemePark:
            lt =  self._browser.find_element_by_tag_name('awakening-selector')
            shadow1 = self.expand_shadow_element(lt)
            lt3 = shadow1.find_elements_by_tag_name('dprd-button') 
            lt3[0].click()
        elif click == ClickType.Resort:
            lt =  self._browser.find_element_by_tag_name('awakening-selector')
            shadow1 = self.expand_shadow_element(lt)
            lt3 = shadow1.find_elements_by_tag_name('dprd-button') 
            lt3[1].click()
        elif click == ClickType.Annual:
            lt =  self._browser.find_element_by_tag_name('awakening-selector')
            shadow1 = self.expand_shadow_element(lt)
            lt3 = shadow1.find_elements_by_tag_name('dprd-button') 
            lt3[2].click()
        elif click == ClickType.NextMonth:
            lt =  self._browser.find_element_by_tag_name('awakening-calendar')
            shadow1 = self.expand_shadow_element(lt)
            lt2 =  shadow1.find_element_by_tag_name('wdat-calendar')
            shadow2 = self.expand_shadow_element(lt2)
            lt3 = shadow2.find_elements_by_tag_name('wdat-calendar-button')
            lt3[1].click()
        elif click == ClickType.PrevMonth:
            lt =  self._browser.find_element_by_tag_name('awakening-calendar')
            shadow1 = self.expand_shadow_element(lt)
            lt2 =  shadow1.find_element_by_tag_name('wdat-calendar')
            shadow2 = self.expand_shadow_element(lt2)
            lt3 = shadow2.find_elements_by_tag_name('wdat-calendar-button')
            lt3[0].click()
        elif click == ClickType.Day:
            lt =  self._browser.find_element_by_tag_name('awakening-calendar')
            shadow1 = self.expand_shadow_element(lt)
            lt2 = shadow1.find_elements_by_tag_name('wdat-date')
            for di in lt2:
                if di.text == str(day):
                    di.click()
        else:
            raise NotImplementedError

        return self._browser.page_source

    def expand_shadow_element(self, element):
        shadow_root = self._browser.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root

    def getAvailability(self):
        #time.sleep(15)

#        lt =  browser.find_element_by_tag_name('awakening-availability-information')
        lt =  self._browser.find_element_by_xpath('//app-availability-calendar/awakening-availability-information')
        
        #time.sleep(5)

        shadow1 = self.expand_shadow_element(lt)
        lt2 = shadow1.find_elements_by_tag_name('div')
         
        result = {"Magic Kingdom" : True, "Animal Kingdom": True, "EPCOT": True, "Hollywood Studios": True}
        #lt2[1] = "magic"
        #lt2[2] = "animal"
        #lt2[3] = 'epcot'
        #lt2[4] = "hollywood"
        p = re.compile('\\ue25a.*')
 
        # for x in range(1,10):
        #     try:
        #         m = p.match(lt2[2].text)
        #         if m:
        #             break
        #         else:
        #             pass
        #     except:
        #         print("Error")



        m = p.match(lt2[1].text)
        if m:
           result["Magic Kingdom"] = False
        else:
           result["Magic Kingdom"] = True
     
        m = p.match(lt2[2].text)
        if m:
           result["Animal Kingdom"] = False
        else:
           result["Animal Kingdom"] = True

        m = p.match(lt2[3].text)
        if m:
           result["EPCOT"] = False
        else:
           result["EPCOT"] = True

        m = p.match(lt2[4].text)
        if m:
           result["Hollywood Studios"] = False
        else:
           result["Hollywood Studios"] = True       
         # \ue25a  - not
        # \ue241  - yes
        return result


    def getByDateRange(self, dateStart, dateEnd):
        if (dateStart < date.today()):
            raise ValueError

        if (dateEnd < date.today()):
            raise ValueError
        
        parkAvail = []

        delta = dateEnd - dateStart         # timedelta

        for i in range(delta.days + 1):
            parkAvail.append(self.checkByDate(dateStart + timedelta(i)))

        return parkAvail

    def checkByDate(self, dateWanted):
        cd = self._currentDate
        #self.waitTill(browser)
        
        if (dateWanted < date.today()):
            raise ValueError
        
        diff = relativedelta.relativedelta(dateWanted, cd)

        if (cd.month == dateWanted.month and diff.months == 0 and diff.years == 0):
            # don't need to switch
            page = self.manipulatePage(ClickType.Day, dateWanted.day)
        else:
            # need to click next button x times
            r = relativedelta.relativedelta(dateWanted, cd)
            #(d1.year - d2.year) * 12 + d1.month - d2.month
            if (r.days < 0 or r.months < 0 or r.years < 0):
                #for x in range(0, ( (r.months+1) + (r.years * 12))):
                for x in range(0, ( (cd.year - dateWanted.year) * 12 + ( cd.month - dateWanted.month) )):
                    page = self.manipulatePage(ClickType.PrevMonth)
            else:     
               for x in range(0, ( (dateWanted.year - cd.year) * 12 + (dateWanted.month - cd.month) )):
                #for x in range(0, ( (r.months+1) + (r.years * 12))):
                    page = self.manipulatePage(ClickType.NextMonth)

            page = self.manipulatePage(ClickType.Day, dateWanted.day)

        pa = self.getAvailability()
        pa.update( {'Date' : dateWanted} )
        self._currentDate = dateWanted
        return pa

    def resetDateToday(self):
        self.checkByDate( date.today())
        #page = self.manipulatePage(browser, ClickType.Day, dateWanted.day)


    def nextAvailableByPark(self, themepark : Park):
        self.resetDateToday()
        self.waitTill()
        
        delta = date(2021,12,31) - date.today()         # timedelta

        found = {"DateFound" : None}


        for i in range(delta.days + 1):
            pa = self.checkByDate(date.today() + timedelta(i))
            if (themepark == Park.MagicKingdom):
                if (pa["Magic Kingdom"] == True):
                    found["DateFound"] = pa["Date"]
                    break
            elif (themepark == Park.Epcot):
                if (pa["EPCOT"] == True):
                    found["DateFound"] = pa["Date"]
                    break
            elif(themepark == Park.HollywoodStudios):
                if (pa["Hollywood Studios"] == True):
                    found["DateFound"] = pa["Date"]
                    break
            elif(themepark == Park.AnimalKingdom):
                if (pa["Animal Kingdom"] == True):
                    found["DateFound"] = pa["Date"]
                    break
            else:
                found["DateFound"] = None

        return found

    def waitTill(self):
        ro = WebDriverWait(self._browser, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//awakening-availability-information"))
        )
        return ro

    def mainProcess(self):

        #options = Options()
        #options.add_argument("--headless")

        #browser = webdriver.Chrome(executable_path=self._chromedriver, options=options)
        #browser.implicitly_wait(10)
 
        
        
        #lt =  browser.find_element_by_tag_name('awakening-selector')
        #shadow1 = self.expand_shadow_element(browser, lt)
       # lt2 = shadow1.find_element_by_tag_name('dprd-radio-group') 
        #shadow2 = self.expand_shadow_element(browser, lt2)
        #lt3 = shadow1.find_elements_by_tag_name('dprd-button') 
        #lt3[1].click()
        
        #dprd-button[contains(@name, "resort")]
        page = self.manipulatePage(ClickType.Annual)
        #cd = date.today()
        try:
            #self.checkByDate(browser, date(2020, 10, 28))
            #pa = self.getByDateRange(browser, date(2020, 8,30), date(2020, 9,3))
            pa = self.nextAvailableByPark(Park.HollywoodStudios)
        except ValueError as e:
            print(f'Invalid Date Passed : {e}')

        #page = self.manipulatePage(browser, ClickType.Day, 28)
        #page = self.manipulatePage(browser, ClickType.NextMonth)
        #page = self.manipulatePage(browser, ClickType.PrevMonth)
        #page = self.getAvailability(browser)
        #results = self.parsePage(page)

        print (pa)
        #self._browser.quit()

def test():
    f = DisneyScraper()
    f.mainProcess()


if __name__ == "__main__": test()      



    