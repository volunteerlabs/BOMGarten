#scraper_digikey.py
# This is the digikey scraper that I made for BOMGarten. Because python is a scripting language
# I decided against implementing an "interface" like with what you'd see in C# or "virtual" like
# you might see in C++.
#
# In order for a scraper to be a scraper it just needs to implement the get functions below and have
# the same signitures.


import wx
import urllib2
import requests
import urllib
from bs4 import BeautifulSoup


#Clean string exists because sometimes when data is scraped from websites you'll get unicode data
# or a string with whitespace. This attempts to return only decent, hardworking, redblooded strings
# back to the main program. The user could of course enter unicode and break the thing, however, but
# for right now I'm going to cross my fingers and hope they don't do that.
def clean_string(str):
    for i in range(0, len(str)):
        try:
            str[i].encode("ascii")
        except:
            #means it's non-ASCII
            str = str.replace(str[i]," ") #replacing it with a single space

    for char in ['\r', '\t', '\n', '\"']:
        str = str.replace(char, '')

    return str.strip()



class digikey_scraper:

    def __init__(self):
        self.search_string = ''
        self.url_string = 'http://digikey.com/scripts/DkSearch/dksus.dll?Detail&name='
        self.response = None

        self.description = None
        self.supplier_name = None
        self.supplier_part_id = None
        self.unit_price = None
        self.part_link = None
        self.datasheet = None
        self.mfg_name = None
        self.mfg_part_id = None
        self.engineering_notes = None


    def set_search_keyword(self, search_string):
        self.search_string = search_string

    def set_search_url(self, url_string):
        self.url_string = url_string

    def scrape(self, search_string):

        if search_string:
            self.set_search_keyword(search_string.strip())
            url = self.url_string + search_string
            if url:
                html = urllib.urlopen(url).read()
                if html:
                    soup = BeautifulSoup(html, "lxml")
                    if soup:

                        temp = soup.find("h1", {"itemprop": "model"})
                        if temp:
                            self.mfg_part_id = temp.text.strip()

                        temp = soup.find("span", {"itemprop": "price"})
                        if temp:
                            self.unit_price = temp.text.strip()

                        temp = soup.find("span", {"itemprop": "name"})
                        if temp:
                            self.mfg_name = temp.text.strip()

                        temp = soup.find("td", {"itemprop": "description"})
                        if temp:
                            self.description = temp.text.strip()

                        temp = soup.find("a", {"class": "lnkDatasheet"})
                        if temp:
                            self.datasheet = temp.get('href')
                            #self.datasheet = temp.text.strip()

                        self.supplier_name = "Digikey"
                        self.supplier_part_id = search_string
                        self.part_link = url
                        self.engineering_notes = "~"

    def get_supplier_name(self):
        return "Digi-Key"

    def get_supplier_part_num(self):
        if self.supplier_part_id:
            retStr = self.supplier_part_id
            retStr = clean_string(retStr)
            return retStr
        else:
            return None

    def get_mfr_part_num(self):
        if self.mfg_part_id:
            retStr = self.mfg_part_id
            retStr = clean_string(retStr)
            return retStr
        else:
            return None

    def get_unit_price(self):
        if self.unit_price:
            retStr = self.unit_price
            retStr = clean_string(retStr)
            return retStr
        else:
            return None

    def get_mfr_name(self):
        if self.mfg_name:
            retStr = self.mfg_name
            retStr = clean_string(retStr)
            return retStr
        else:
            return None

    def get_description(self):
        if self.description:
            retStr = self.description
            retStr = clean_string(retStr)
            return retStr
        else:
            return None

    def get_partlink(self):
        if self.part_link:
            retStr = self.part_link
            retStr = clean_string(retStr)
            return retStr
        else:
            return None

    def get_datasheet(self):
        if self.datasheet:
            retStr = self.datasheet
            retStr = clean_string(retStr)
            return retStr
        else:
            return None
