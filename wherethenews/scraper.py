#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:03:14 2020

@author: ryepenchi
"""
import sys, time
from datetime import datetime
from dateutil import parser as dp

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

import spacy
from geopy.geocoders import Nominatim

from utilities import log, args, sites
from dbconfig import db, Article, Place

class Scraper:
    _instance = None
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

    def scrape_article(self, link):
        self.driver.get(link)
        if "privacywall" in self.driver.current_url:
            self.driver.find_element_by_css_selector(
                ".js-privacywall-agree").click()
        log("Reached ", self.driver.current_url)

        # ID
        id = int(link[33:46])
        # Sanity Check for duplicate
        l = db.session.query(Article.id).all()
        existing_ids = [item for sublist in l for item in sublist]
        if id in existing_ids:
            return
        # TITLE
        title = self.driver.find_element_by_class_name(
            "article-title").text
        title = title.replace("'","''")
        # SCRAPE DATE
        scrape_date = datetime.now()
        # SUBTITLE
        subtitle = self.driver.find_element_by_class_name(
            "article-subtitle").text
        subtitle = subtitle.replace("'","''")
        # PUB DATE
        pub_date = self.driver.find_element_by_tag_name(
            "time").get_attribute("datetime")[:-1]
        pub_date = datetime.strptime(pub_date,"%Y-%m-%dT%H:%M")
        # CATEGORIES
        categories = self.driver.find_elements_by_xpath(
            "//nav[@class='site-contextnavigation-breadcrumbs-nav']/a")
        cats = [cat.get_attribute("title") for cat in categories[1:]]
        cats = ", ".join(cats)
        # BODY
        body = []
        if "pro-und-kontra" in link:
            article_body = self.driver.find_element_by_xpath(
                "//div[@class='article-body']")
            paragraphs = article_body.find_elements_by_tag_name("p")
            for paragraph in paragraphs:
                body.append(paragraph.text)
        else:
            paragraphs = self.driver.find_elements_by_xpath(
                "//div[@class='article-body']/*")
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
        br = []
        uids = []
        for ent in ents:
            # Get rid of single letter ents and date ents
            if len(ent) < 3:
                continue
            try:
                if type(dp.parse(ent)) == datetime:
                    continue
            except Exception:
                pass
            r = self.geolocator.geocode(ent)
            # Conditions whether new place was found, is new or relevat
            if r:
                c1 = r.raw["place_id"] not in uids
                c2 = r.raw["importance"] > 0.5
                if all((r, c1, c2)):
                    uids.append(r.raw["place_id"])
                    place = {"word": ent,
                        "address": r.raw["display_name"],
                        "geo": r.point,
                        "place_id": r.raw["place_id"]
                        }
                    br.append(place)

        # ARTICLE ENTRY
        article = Article(
            id = id,
            title = title,
            subtitle = subtitle,
            link = link,
            cats = cats,
            pub_date = pub_date,
            scrape_date = scrape_date,
            words = ",".join(ents),
            body = body
        )

        # PLACES ENTRIES
        # für jeden neuen Ort nen Eintrag im places table machen
        l = db.session.query(Place.id).all()
        existing_ids = [item for sublist in l for item in sublist]

        for place in br:
            if place["place_id"] not in existing_ids:
                # make entry in places
                place = Place(
                    id = place["place_id"],
                    word = place["word"],
                    place_name = place["address"],
                    lat = place["geo"].latitude,
                    lon = place["geo"].longitude
                )
                article.places.append(place)
        db.session.add(article)
        db.session.commit()
        self.cnt += 1

    def scrape_for_links(self):
        # Scrape and Filter for new article Links
        self.driver.get(self.site)
        if "privacywall" in self.driver.current_url:
            self.driver.find_element_by_css_selector(
                ".js-privacywall-agree").click()
        log("Reached " + self.driver.current_url)

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
            nonarticle = ["sudoku", "kreuzwortraetsel", "livebericht"]
            nonarticle = any([n in link for n in nonarticle])
            if not nonarticle:
                links.append(link)

        l = db.session.query(Article.id).all()
        if l:
            existing_ids = [item for sublist in l for item in sublist]
            log(str(len(existing_ids)) + " articles already in DB")
            # print(existing_ids)
            links = [l for l in links if int(l[33:46]) not in existing_ids]
            # print(links)
        log(f"Found {len(links)} new articles")
        self.links = list(set(links))
        return True

if __name__ == "__main__":
    log("Scraper started")
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
            for link in links[:5]:
                scraper.scrape_article(link)
    log("Scraped {} articles from {}".format(scraper.cnt, scraper.site))
