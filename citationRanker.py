import json
import time

import nltk
import pandas as pd
import requests
from bs4 import BeautifulSoup
import argparse
from tqdm import tqdm

SLEEP_TIME = 1.5

# Websession Parameters
GSCHOLAR_URL = 'https://scholar.google.com/scholar?start={}&q={}&hl=en&as_sdt=0,5'
ROBOT_KW = ['unusual traffic from your computer network', 'not a robot']


def get_citations(content):
    out = 0
    for char in range(0, len(content)):
        if content[char:char + 9] == 'Cited by ':
            init = char + 9
            for end in range(init + 1, init + 6):
                if content[end] == '<':
                    break
            out = content[init:end]
    return int(out)


def get_year(content):
    for char in range(0, len(content)):
        if content[char] == '-':
            out = content[char - 5:char - 1]
    if not out.isdigit():
        out = 0
    return int(out)


def setup_driver(driver_path=None):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.common.exceptions import StaleElementReferenceException
    except Exception as e:
        print(e)
        print("Please install Selenium and chrome webdriver for manual checking of captchas")

    print('Loading...')
    chrome_options = Options()
    chrome_options.add_argument("disable-infobars")
    if driver_path is None:
        driver_path = "./chromedriver"
    driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
    return driver


def get_author(content):
    for char in range(0, len(content)):
        if content[char] == '-':
            out = content[2:char - 1]
            break
    return out


def get_element(driver, xpath, attempts=5, _count=0):
    '''Safe get_element method with multiple attempts'''
    try:
        element = driver.find_element_by_xpath(xpath)
        return element
    except Exception as e:
        if _count < attempts:
            time.sleep(1)
            get_element(driver, xpath, attempts=attempts, _count=_count + 1)
        else:
            print("Element not found")


def get_content_with_selenium(url, drive_path=None):
    if 'driver' not in globals():
        global driver
        driver = setup_driver(drive_path)
    driver.get(url)

    # Get element from page
    el = get_element(driver, "/html/body")
    c = el.get_attribute('innerHTML')

    if any(kw in el.text for kw in ROBOT_KW):
        input("Solve captcha manually and press enter here to continue...")
        el = get_element(driver, "/html/body")
        c = el.get_attribute('innerHTML')

    return c.encode('utf-8')


class PaperTitle():
    def __init__(self, conf_name, year_start=2010, year_end=None,
                 output_file=None, keyword=None, driver_path=None):
        self._conf_name = conf_name.lower().split(",")
        self._conf_name = list(map(lambda x: x.strip(), self._conf_name))
        if year_end is None:
            year_end = year_start
        self._years = range(year_start, year_end + 1)
        self._output_file = output_file
        self._driver_path = driver_path

        self._session = requests.Session()
        if keyword is not None:
            self._keyword = keyword.lower().split(",")
            self._keyword = list(map(lambda x: x.strip(), self._keyword))
        self.paper_info_pd = None

    def save_paper_info(self, paper_info_list):
        paper_info_pd = pd.DataFrame(paper_info_list, columns=["title", "citation", "link", "conf", "year"])
        paper_info_pd["citation"] = paper_info_pd["citation"].astype(int)
        paper_info_pd["year"] = paper_info_pd["year"].astype(int)
        paper_info_pd = paper_info_pd.sort_values(by=["citation", "year"], ascending=False)
        if self.paper_info_pd is None:
            self.paper_info_pd = paper_info_pd
        else:
            self.paper_info_pd = pd.concat([self.paper_info_pd, paper_info_pd])

    def get_paper_info(self, paper_title):
        url = GSCHOLAR_URL.format(str(0), paper_title.replace(' ', '+'))
        while True:
            try:
                page = self._session.get(url)
                break
            except requests.exceptions.ConnectionError:
                pass
        c = page.content
        if any(kw in c.decode('ISO-8859-1') for kw in ROBOT_KW):
            # print("Robot checking detected, handling with selenium (if installed)")
            try:
                c = get_content_with_selenium(url, drive_path=self._driver_path)
            except Exception as e:
                print("No success. The following error was raised:")
                print(e)
        # Create parser
        soup = BeautifulSoup(c, 'html.parser')
        # Get stuff
        mydivs = soup.findAll("div", {"class": "gs_r"})

        try:
            div = mydivs[0]
            link = div.find('h3').find('a').get('href')
            title = div.find('h3').find('a').text
            citation = get_citations(str(div.format_string))
        except Exception as e:
            return None
        if nltk.edit_distance(paper_title.lower(), title.lower()) > 10:
            return None
        return title, citation, link

    def get_paper_title_list(self, conf, year):
        paper_title_list = []
        first_hix_index = 0
        while True:
            # The first hit index. DBLP retrieve at most 1000 items once.

            url = "https://dblp.org/search/publ/api?q=conf%2F" + conf + "%20" + \
                  str(year) + "&h=1000&f=" + str(first_hix_index) + "&format=json"
            r = requests.get(url)
            c = r.content
            num = json.loads(c)['result']['hits']["@sent"]
            if not int(num) > 0:
                break
            first_hix_index += 1000
            content = json.loads(c)['result']['hits']['hit']
            for info in content:
                try:
                    paper_info = info["info"]
                    if type(paper_info["venue"]) is list:
                        paper_info["venue"] = " ".join(paper_info["venue"])
                    if conf.lower() in paper_info["venue"].lower() and paper_info["year"] == str(year):
                        if self._keyword is not None:
                            keyword_flag = False
                            for keyword in self._keyword:
                                if not keyword in paper_info["title"].lower():
                                    keyword_flag = True
                                    break
                            if keyword_flag:
                                continue
                        paper_title_list.append(paper_info["title"])
                except KeyError:
                    continue
        return paper_title_list

    def get_paper_list_by_conf_year(self, conf, year):
        paper_title_list = self.get_paper_title_list(conf, year)
        paper_info_list = []
        # pd.DataFrame(paper_info_list, columns=["title", "citation", "link"])
        for paper_title in tqdm(paper_title_list, desc=conf+"_"+str(year), ):
            paper_info = self.get_paper_info(paper_title)
            if paper_info is not None:
                paper_info = list(paper_info) + [conf, year]
                paper_info_list.append(paper_info)
            time.sleep(SLEEP_TIME)
        self.save_paper_info(paper_info_list)
        return paper_info_list

    def get_paper_list(self):
        for conf in self._conf_name:
            for year in self._years:
                self.get_paper_list_by_conf_year(conf, year)
        if self._output_file is None:
            self._output_file = "_".join(self._conf_name) + "__" + str(self._years[0]) + "to" + str(
                self._years[-1]) + ".csv"
        self.paper_info_pd = self.paper_info_pd.sort_values(by=["citation", "year"], ascending=False)
        self.paper_info_pd.to_csv(self._output_file, index=False)
        print("save the output to %s" % self._output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conferences", default="",
                        type=str, help="The abbr. of conferences, separated by comma(,)")
    # "./chromedriver"
    parser.add_argument("-y", "--year_start", default=2020,
                        type=int, help="The start year")
    parser.add_argument("-e", "--year_end", default=None,
                        type=int, help="The end year")
    parser.add_argument("-o", "--output_file", default=None,
                        required=False,
                        type=str, help="The output file name. ")
    parser.add_argument("-kw", "--keyword", default=None,
                        required=False,
                        type=str, help="Search paper titles by keywords, separated by comma(,)")
    parser.add_argument("--driver", default=None,
                        required=False,
                        type=str, help="The path for chromedriver, default is under current folder './chromedriver' ")
    args = parser.parse_args()
    pt = PaperTitle(conf_name=args.conferences, year_start=args.year_start, year_end=args.year_end,
                    output_file=args.output_file, keyword=args.keyword, driver_path=args.driver)
    pt.get_paper_list()
# pt = PaperTitle("naacl,icml,iclr,nips", 2019, 2020)
# pt.get_paper_list()
# paper_title = 'Sequence and Time Aware Neighborhood for Session-based Recommendations: STAN'
