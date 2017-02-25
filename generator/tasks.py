#
# tasks.py
#
# generate cube-drone.com from an RSS file that we nab from Threepanel
#

import json
import os

import feedparser
import invoke
from jinja2 import Environment, FileSystemLoader, select_autoescape
from invoke import task

PAPERTRAIL_HOST = "logs3.papertrailapp.com"
PAPERTRAIL_PORT = "14163"
FEED_URL = 'https://threepanel.com/t/cube-drone/18.rss';
PATH = '.'


@task(optional=['feed_url', 'path'])
def generate(ctx, feed_url=None, path=None):
    """
    Generate cube-drone.com from an RSS file
    """

    if not feed_url:
        feed_url = FEED_URL

    if not path:
        path = PATH

    r = feedparser.parse(feed_url)
    feed = r.feed
    feed['favicon'] = "https://d24ju8re1w4x9e.cloudfront.net/original/2X/e/e4616b104f34924e0631cedf6e7fbf5ee523125e.png"
    feed['subtitle'] = "Comics about Code"
    feed['entries'] = r.entries

    print(json.dumps(feed, indent=4))

    ## jinja2

    env = Environment(loader=FileSystemLoader('./'), autoescape=select_autoescape(['html', 'xml']))

    template = env.get_template('index.j2')

    rendered_template = template.render(feed)

    index_filename = os.path.join(path, 'index.html')

    with open('index.html', 'w') as f:
        f.write(rendered_template)

rewrite_rules = {
        'rss.xml': 'https://threepanel.com/t/cube-drone/18.rss',
        'comics': 'http://cube-drone.com',
        'comics/archives': 'http://cube-drone.com',
        'comics/blog': 'https://threepanel.com/c/category',
        'comics/c/subscribe': 'https://threepanel.com/',
        'comics/archives': 'http://cube-drone.com',
        'comics/blog': 'https://threepanel.com/c/category',
        'comics/c/subscribe': '',
        'comics/c/relentless-persistence': '',
        'comics/c/many-factor-authentication': '',
        'comics/c/how-it-feels-to-learn-javascript-in-2016': '',
        'comics/c/the-songs-of-programming': '',
        'comics/c/civilization': '',
        'comics/c/professionalism': '',
        'comics/c/social-media-math': '',
        'comics/c/encapsulation': '',
        'comics/c/bug-bestiary-the-beezlebug': '',
        'comics/c/http-status-codes': '',
        'comics/c/pickled-pythons': '',
        'comics/c/version-sacrifice': '',
        'comics/c/requirements-mambo': '',
        'comics/c/fine-art': '',
        'comics/c/if-programming-languages-were-vehicles': '',
        'comics/c/if-programming-languages-were-vehicles-ii': '',
        'comics/c/if-programming-languages-were-vehicles-iii': '',
        'comics/c/if-programming-languages-were-vehicles-iv': '',
        'comics/c/tux-in-space': '',
        'comics/c/poop-helmet': '',
        'comics/c/up-up-and-away': '',
        'comics/c/cutting-the-gordian-knot': '',
        'comics/c/office-lan-party-planning': '',
        'comics/c/tone-deaf': '',
        'comics/c/vulnerability': '',
        'comics/c/dont-cry-cube-drone': '',
        'comics/c/dont-prod-the-bear': '',
        'comics/c/pep8-vs-v05': '',
        'comics/c/severance-package': '',
        'comics/c/some-like-it-hot': '',
        'comics/c/sometimes-why': '',
        'comics/c/the-only-way': '',
        'comics/c/yaoi': '',
        'comics/c/1000-kg': '',
        'comics/c/cyberpunk-2016': '',
        'comics/c/going-feral': '',
        'comics/c/its-harder-in-a-distributed-environment': '',
        'comics/c/missing-the-point': '',
        'comics/c/variations-on-a-theme': '',
        'comics/c/a-funny-thing-happened-on-the-way-to-the-forum': '',
        'comics/c/a-fun-prank': ''}

@task()
def generate_nginx_config(ctx):
    """
    Generate the entire nginx configuration for this service.
    """
    pass
