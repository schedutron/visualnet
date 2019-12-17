# Main Script
import ssl
import sys
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests
from sqlalchemy.exc import IntegrityError
from app import db

if len(sys.argv) < 3:
    print("Usage: python3 -m spider.spider http://some.doma.in num_pages")
    quit()
web_url_top, num_pages = sys.argv[1], int(sys.argv[2])


if len(web_url_top) < 1:
    web_url_top = "http://lnmiit.ac.in"
if ( web_url_top.endswith('/') ) : web_url_top = web_url_top[:-1]

# Check to see if we are already in progress...
res = db.session.execute('SELECT id, url FROM webs WHERE url = :wut', {'wut': web_url_top})
try:
    web_id, web_url_top = next(res)
    print("Restarting existing crawl.")
except StopIteration:
    web = web_url_top.split('/')[2]
    web = web_url_top[:web_url_top.find(web)+len(web)]

    if len(web) > 1:
        # INSERT OR IGNORE...
        try:
            db.session.execute('INSERT INTO webs (url) VALUES (:web)', {'web': web})
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        res = db.session.execute('SELECT id FROM webs WHERE url = :web', {'web': web})
        web_id = next(res)[0]

        try:
            db.session.execute('INSERT INTO pages (url, html, new_rank, web_id) VALUES (:web, NULL, 1.0, :wi)', {'web': web, 'wi': web_id})
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


res = db.session.execute('SELECT id, url FROM webs WHERE url = :wut', {'wut': web_url_top})
web_id, web_url_top = next(res)

if num_pages < 1:
    num_pages = 1
for _ in range(num_pages):

    res = db.session.execute('SELECT id, url FROM pages WHERE html is NULL and error is NULL AND web_id = :wi ORDER BY RANDOM() LIMIT 1', {'wi': web_id})
    try:
        row = next(res)
        #print(row)
        fromid = row[0]
        url = row[1]
    except:
        print('No unretrieved HTML pages found')
        break

    print(fromid, url, end=' ')

    # If we are retrieving this page, there should be no links from it
    db.session.execute('DELETE from links WHERE from_id=:fi', {'fi': fromid})
    db.session.commit()
    try:
        r = requests.get(url)

        html = r.text
        if not r.ok:
            print("Error on page:", r.status_code)
            db.session.execute('UPDATE pages SET error= :sc WHERE url= :url', {'sc': r.status_code, 'url': url})
            db.session.commit()

        if 'text/html' != r.headers.get('Content-Type').split(";")[0]:
            print("\nIgnore non text/html page")
            db.session.execute('DELETE FROM pages WHERE url=:url', {'url': url})
            db.session.execute('UPDATE pages SET error=0 WHERE url=:url', {'url': url})
            db.session.commit()
            continue

        print('('+str(len(html))+')')

        soup = BeautifulSoup(html, "html.parser")
    except KeyboardInterrupt:
        print()
        print('Program interrupted by user...')
        break
    except:
        print("Unable to retrieve or parse page")
        db.session.execute('UPDATE pages SET error=-1 WHERE url=:url', {'url': url})
        db.session.commit()
        continue

    try:
        db.session.execute('INSERT INTO pages (url, html, new_rank, web_id) VALUES ( :url, NULL, 1.0, :wi)', {'url': url, 'wi': web_id})
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    db.session.execute('UPDATE pages SET html=:html WHERE url=:url', {'html': str(memoryview(html.encode('utf-8'))), 'url': url})
    db.session.commit()

    # Retrieve all of the anchor tags
    tags = soup('a')
    count = 0
    for tag in tags:
        href = tag.get('href', None)
        if ( href is None ) : continue
        # Resolve relative references like href="/contact"
        up = urlparse(href)
        if ( len(up.scheme) < 1 ) :
            href = urljoin(url, href)
        ipos = href.find('#')
        if ( ipos > 1 ) : href = href[:ipos]
        if ( href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif') ) : continue
        if ( href.endswith('/') ) : href = href[:-1]
        # print href
        if ( len(href) < 1 ) : continue

		# Check if the URL is in the web
        domain = web_url_top.split('/')[2]
        if web_url_top not in href:
            continue

        try:
            db.session.execute('INSERT INTO pages (url, html, new_rank, web_id) VALUES ( :url, NULL, 1.0, :wi)', {'url': href, 'wi': web_id})
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        count = count + 1

        res = db.session.execute('SELECT id FROM pages WHERE url=:url LIMIT 1', {'url': href})
        try:
            row = next(res)
            toid = row[0]
        except:
            print('Could not retrieve id')
            continue

        try:
            # print fromid, toid
            db.session.execute('INSERT INTO links (from_id, to_id) VALUES (:fi, :ti)', {'fi': fromid, 'ti': toid})
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    print(count)
