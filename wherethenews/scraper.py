#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:03:14 2020

@author: ryepenchi
"""
import sys, time
from datetime import datetime
#from random import shuffle

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

import spacy
from geopy.geocoders import Nominatim
# import logging

from utilities import log, cursor, args, sites
import config

class Scraper:
    _instance = None
    cfg = config.cfg
    driver = None
    site = None
    number = 0
    links = []
    cnt = 0

    def __init__(self, args):
        self._instance = self
        if args.site:
            site = args.site.lower()
            if site in sites:
                self.site = sites[site]
        else:
            # Default site
            self.site = sites["derstandard"]

    def __enter__(self):
        opts = Options()
        opts.headless = True
        self.driver = Chrome(options=opts)
        self.nlp = spacy.load('de_core_news_md', disable=['parser', 'tagger'])
        self.geolocator = Nominatim(user_agent="wapapp")

    def __exit__(self, exception_type, exception_value, traceback):
        self.driver.quit()

    def test_run(self):
        with self.driver as driver:
            driver.get("http://www.google.com")
            print(driver.current_url)

    def test_dbconn(self):
        with cursor(self.cfg) as c:
            c.execute("SHOW TABLES;")
            print(list(x[0] for x in c.fetchall()))
            c.execute("DESC articles;")
            print(list(" ".join(str(y) for y in x) for x in c.fetchall()))

    def scrape_article(self, link):
        self.driver.get(link)
        if "privacywall" in self.driver.current_url:
            self.driver.find_element_by_css_selector(".js-privacywall-agree").click()
        print("Reached ", self.driver.current_url)

        # ID
        id = link[33:46]
        # TITLE
        title = self.driver.find_element_by_class_name("article-title").text
        title = title.replace("'","''")
        # SCRAPE DATE
        scrape_date = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M")
        # SUBTITLE
        subtitle = self.driver.find_element_by_class_name("article-subtitle").text
        subtitle = subtitle.replace("'","''")
        # PUB DATE
        pub_date = self.driver.find_element_by_tag_name("time").get_attribute("datetime")[:-1]
        # CATEGORIES
        categories = self.driver.find_elements_by_xpath("//nav[@class='site-contextnavigation-breadcrumbs-nav']/a")
        cats = [cat.get_attribute("title") for cat in categories[1:]]
        cats = ", ".join(cats)
        # BODY
        body = []
        if "pro-und-kontra" in link:
            article_body = self.driver.find_element_by_xpath("//div[@class='article-body']")
            paragraphs = article_body.find_elements_by_tag_name("p")
            for paragraph in paragraphs:
                body.append(paragraph.text)
        else:
            paragraphs = self.driver.find_elements_by_xpath("//div[@class='article-body']/*")
            #print("Getting ps and h3s")
            for paragraph in paragraphs:
                if paragraph.get_property("localName") in ("p", "h3"):
                    #print("Escaped...\n", text)
                    body.append(paragraph.text)
        #print("joining ps and h3s ")
        body = "\n\n".join(body)
        #print("replacing shit ")
        body = body.replace("'","''")

        # NLP
        doc = self.nlp(body)
        ents = set([ent.text for ent in doc.ents if ent.label_ == "LOC"])

        # GEOCODE
        br = list()
        for ent in ents:
            r = self.geolocator.geocode(ent)
            if r:
                if r.raw["importance"] > 0.5:
                    place = {"word": ent,
                        "address": r.raw["display_name"],
                        "geo": r.point,
                        "place_id": r.raw["place_id"]
                        }
                    br.append(place)
        # PLACES ENTRIES
        with cursor(self.cfg) as c:
            # für jeden neuen Ort nen Eintrag im places table machen
            query_string = """SELECT geonameid FROM places;"""
            c.execute(query_string)
            l = c.fetchall()
            if l:
                existing_ids = [item for sublist in l for item in sublist]

            for place in br:
                if place["place_id"] not in existing_ids:
                    # make entry in places
                    query_string = f"""INSERT INTO places (geonameid, place_name, lat, lon) VALUES ('{place["place_id"]}', '{place["word"]}', '{place["geo"].latitude}', '{place["geo"].longitude}');"""
                    c.execute(query_string)
        # ARTICLE ENTRY
        with cursor(self.cfg) as c:
            query_string = f"""INSERT INTO articles (id, title, subtitle, link, cats, 
                                    pub_date, scrape_date, body) 
                            VALUES ('{id}','{title}','{subtitle}','{link}','{cats}',
                                    '{pub_date}','{scrape_date}','{body}')"""
            c.execute(query_string)
            self.cnt += 1
        # MENTIONS ENTRIES
        with cursor(self.cfg) as c:
            for place in br:
                # make entry in mentions
                query_string = f"""INSERT INTO mentions (article_id, place_id) VALUES ('{id}', '{place["place_id"]}')"""
                c.execute(query_string)



    def scrape_for_links(self):
        # Scrape and Filter for new article Links
        self.driver.get(self.site)
        if "privacywall" in self.driver.current_url:
            self.driver.find_element_by_css_selector(".js-privacywall-agree").click()
        print("Reached ", self.driver.current_url)

        results = self.driver.find_elements_by_tag_name("article")
        tries = 0
        while len(results) == 0 and tries < 10:
            tries += 1
            #print("Refreshing...")
            self.driver.refresh()
            time.sleep(3)
            results = self.driver.find_elements_by_tag_name("article")
        #print(len(results), "articles found...")
        
        links = []
        for r in results:
            link = str(r.find_element_by_tag_name("a").get_attribute("href"))
            links.append(link)

        with cursor(self.cfg) as c:
            c.execute("SELECT id FROM articles;")
            l = c.fetchall()
        if l:
            existing_ids = [item for sublist in l for item in sublist]
            print(len(existing_ids), " articles already in DB")
            #print(existing_ids)
            links = [l for l in links if l[33:46] not in existing_ids]
            #print(links)
        links = [l for l in links if not ("sudoku" in l or "kreuzwortraetsel" in l or "livebericht" in l)]
        print(f"Found {len(links)} new articles")
        self.links = list(set(links))
        return True

if __name__ == "__main__":
    scraper = Scraper(args)
    with scraper:
        if args.all:
            scraper.scrape_for_links()
            for link in scraper.links:
                scraper.scrape_article(link)
        elif args.this:
            scraper.scrape_article(args.this)
        elif args.number:
            scraper.scrape_for_links()
            links = scraper.links
            for link in links[:args.number+1]:
                scraper.scrape_article(link)
        else:
            scraper.scrape_for_links()
            # Get 5 articles from derStandard by default
            links = scraper.links
            for link in links[:6]:
                scraper.scrape_article(link)
            #s.test_dbconn()
    print("Scraped {} articles from {}".format(scraper.cnt, scraper.site))
