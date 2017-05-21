import requests
from bs4 import BeautifulSoup, SoupStrainer
import dateparser
from app import app

only_information = SoupStrainer("div", {"itemprop": True})
headers = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (compatible; {})".format(app.config["CONTACT_INFO"])
}

def clean_text(dirty_text):
    return dirty_text.strip()

def parse_date(date_str):
    return dateparser.parse(date_str)

def get_information(android_id):
    app.logger.info("Getting update for {}".format(android_id))
    result = requests.get("https://play.google.com/store/apps/details?id={}".format(android_id), headers=headers)
    try:
        result.raise_for_status()
        #TODO: add logging
    except:
        app.logger.info("Update for {} failed".format(android_id))
        return None
    c = result.text
    soup = BeautifulSoup(c, "lxml", parse_only=only_information)

    date_tag = soup.find("div", {"itemprop": "datePublished"})
    if date_tag:
        date_str = clean_text(date_tag.text)
        date = parse_date(date_str)
    else:
        return None
    versiontag = soup.find("div", {"itemprop": "softwareVersion"})
    if versiontag:
        version = clean_text(soup.find("div", {"itemprop": "softwareVersion"}).text)
    else:
        version = date.strftime("%Y.%m.%d")
    return({
        "published": date,
        "version": version
    })