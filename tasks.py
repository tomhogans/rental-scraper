import re
import time
import os.path

import requests
import lxml.html


DATA_PATH = 'var/'


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
