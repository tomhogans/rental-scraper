import re
import time
import os.path
from collections import namedtuple

import requests
import lxml.html


DATA_PATH = 'var/'

Post = namedtuple('Post',
                  ['url', 'price', 'title', 'location', 'photos',
                   'bedrooms', 'bathrooms', 'sqft', 'available_date',
                   'extra_info', 'body', 'map_link', 'posted_at'])


def parse_post(html_string):
    """ Parses HTML content of a posting and returns a Post namedtuple
    """
    root = lxml.html.fromstring(html_string)
    post_url = root.xpath("//link[@rel='canonical']/@href")
    price = root.xpath("//span[@class='price']/text()")
    title = root.xpath("//span[@id='titletextonly']/text()")
    location = root.xpath("//small/text()")
    bedrooms = root.xpath("(//p[@class='attrgroup'])[1]/span[starts-with(text(),'BR')]/b/text()")
    bathrooms = root.xpath("(//p[@class='attrgroup'])[1]/span[text()='Ba']/b/text()")
    sqft = root.xpath("(//p[@class='attrgroup'])[1]/span[text()='ft']/b/text()")
    available_date = root.xpath("//span[@class='housing_movein_now property_date']/@date")
    photos = root.xpath("//div[@id='thumbs']//a/@href")
    extra_info = root.xpath("(//p[@class='attrgroup'])[2]//span/text()")
    body = root.xpath("//section[@id='postingbody']/text()")
    timestamps = root.xpath("//time/@datetime")
    map_link = root.xpath("//a[text()='google map']/@href")
    return Post(post_url[0],
                price[0],
                title[0],
                location[0][2:-1] if location else None,
                photos,
                bedrooms[0] if bedrooms else None,
                bathrooms[0] if bathrooms else None,
                sqft[0] if sqft else None,
                available_date[0] if available_date else None,
                extra_info,
                body[0].strip(),
                map_link[0] if map_link else None,
                timestamps[-1] if timestamps else None)


def parse_listings(html_string):
    """ Parses HTML content and extracts listing IDs
    """
    root = lxml.html.fromstring(html_string)
    links = [e.attrib['href'] for e in root.xpath('//a')
             if e.attrib['href'].startswith('/apa/')]
    ids = [re.findall('/apa/([0-9]+).html', u) for u in links]
    return [i[0] for i in ids if i]  # return flattened list


def fetch_listing(city, listing_id):
    """ Requests HTML content for `listing_id` in the specified `city`
    """
    url = "http://{}.craigslist.org/apa/{}.html".format(city, listing_id)
    time.sleep(5)
    return requests.get(url).content


def find_most_recent_post_id():
    modified_times = [(os.path.getmtime(f), f) for f in os.listdir(DATA_PATH)]
    last_modified_file = max(modified_times)[1] if modified_times else ''
    return last_modified_file.partition('.')[0]


def get_listings(city):
    url = "http://{}.craigslist.org/search/apa".format(city)
    resp = requests.get(url)
    listing_ids = parse_listings(resp.content)

    for listing_id in listing_ids:
        filename = '{}{}.html'.format(DATA_PATH, listing_id)
        if os.path.isfile(filename):
            continue
        html = fetch_listing(city, listing_id)
        open(filename, 'w').write(html.decode('utf-8'))


if __name__ == '__main__':
    get_listings('philadelphia')
