#
# tasks.py
#
# generate cube-drone.com from an RSS file that we nab from Threepanel
#

import json
import os
import random
import datetime

import feedparser
import invoke
from jinja2 import Environment, FileSystemLoader, select_autoescape
from invoke import task

PAPERTRAIL_HOST = "logs3.papertrailapp.com"
PAPERTRAIL_PORT = "14163"
FEED_URL = 'https://threepanel.com/t/cube-drone/18.rss';
PATH = '.'

PATTERNS = ['agsquare',
    'back_pattern',
    'black_lozenge',
    'congruent_outline',
    'ecailles',
    'escheresque_ste',
    'footer_lodyas',
    'grey',
    'grey_wash_wall',
    'hexabump',
    'honey_im_subtle',
    'knitting250px',
    'linedpaper',
    'mochaGrunge',
    'navy_blue',
    'pixel_weave',
    'ps_neutral',
    'pw_maze_black',
    'pw_maze_white',
    'retina_dust',
    'shattered',
    'small_steps',
    'sneaker_mesh_fabric',
    'swirl',
    'triangular',
    'use_your_illusion',
    'wild_oliva']

LIGHT_PATTERNS = ['agsquare',
            'back_pattern',
            'ecailles',
            'grey',
            'grey_wash_wall',
            'honey_im_subtle',
            'knitting_250px',
            'linedpaper',
            'mochaGrunge',
            'navy_blue',
            'pixel_weave',
            'ps_neutral',
            'pw_maze_white',
            'retina_dust',
            'shattered',
            'small_steps',
            'sneaker_mesh_fabric',
            'swirl',
            'triangular']

DARK_PATTERNS = ['black_lozenge',
        'congruent_outline',
        'escheresque_ste',
        'footer_lodyas',
        'grey_wash_wall',
        'hexabump',
        'mochaGrunge',
        'navy_blue',
        'pw_maze_black',
        'user_your_illusion',
        'wild_oliva']

REWRITE_RULES = {
        'rss.xml': 'https://threepanel.com/t/cube-drone/18.rss',
        'comics': 'http://cube-drone.com',
        'comics/archives': 'http://cube-drone.com',
        'comics/blog': 'https://threepanel.com/c/category',
        'comics/c/subscribe': 'https://threepanel.com/',
        'comics/archives': 'http://cube-drone.com',
        'comics/blog': 'https://threepanel.com/c/category',
        'comics/c/relentless-persistence': 'https://threepanel.com/t/cube-drone/18/70',
        'comics/c/version-sacrifice': 'https://threepanel.com/t/cube-drone/18/71',
        'comics/c/many-factor-authentication': 'https://threepanel.com/t/cube-drone/18/156',
        'comics/c/how-it-feels-to-learn-javascript-in-2016': 'https://threepanel.com/t/cube-drone/18/152',
        'comics/c/the-songs-of-programming': 'https://threepanel.com/t/cube-drone/18/155',
        'comics/c/civilization': 'https://threepanel.com/t/cube-drone-video-games/61/5',
        'comics/c/professionalism': 'https://threepanel.com/t/cube-drone/18/154',
        'comics/c/social-media-math': 'https://threepanel.com/t/cube-drone/18/153',
        'comics/c/encapsulation': 'https://threepanel.com/t/cube-drone/18/140',
        'comics/c/bug-bestiary-the-beezlebug': 'https://threepanel.com/t/cube-drone/18/151',
        'comics/c/http-status-codes': 'https://threepanel.com/t/cube-drone/18/150',
        'comics/c/pickled-pythons': 'https://threepanel.com/t/cube-drone/18/102',
        'comics/c/fine-art': 'https://threepanel.com/t/cube-drone/18/104',
        'comics/c/if-programming-languages-were-vehicles': 'https://threepanel.com/t/cube-drone/18/39',
        'comics/c/if-programming-languages-were-vehicles-ii': 'https://threepanel.com/t/cube-drone/18/39',
        'comics/c/if-programming-languages-were-vehicles-iii': 'https://threepanel.com/t/cube-drone/18/39',
        'comics/c/if-programming-languages-were-vehicles-iv': 'https://threepanel.com/t/cube-drone/18/39',
        'comics/c/the-blame-game': 'https://threepanel.com/t/cube-drone/18/27',
        'comics/c/ingenuity-of-sorts': 'https://threepanel.com/t/cube-drone/18/20',
        'comics/c/requirements-mambo': 'https://threepanel.com/t/secret-archives/62',
        'comics/c/tux-in-space': 'https://threepanel.com/t/secret-archives/62',
        'comics/c/up-up-and-away': 'https://threepanel.com/t/secret-archives/62',
        'comics/c/office-lan-party-planning': 'https://threepanel.com/t/secret-archives/62',
        'comics/c/dont-cry-cube-drone': 'https://threepanel.com/t/secret-archives/62',
        'comics/c/sometimes-why': 'https://threepanel.com/t/secret-archives/62',
        'comics/c/the-only-way': 'https://threepanel.com/t/secret-archives/62',
        'comics/c/going-feral': 'https://threepanel.com/t/cube-drone/18/49',
        'comics/c/poop-helmet': 'https://threepanel.com/t/cube-drone/18/87',
        'comics/c/still-crazy-after-all-these-years': 'https://threepanel.com/t/cube-drone/18/75',
        'comics/c/art-of-war': 'https://threepanel.com/t/cube-drone/18/66',
        'comics/c/openstack': 'https://threepanel.com/t/cube-drone/18/61',
        'comics/c/progress': 'https://threepanel.com/t/cube-drone/18/57',
        'comics/c/cutting-the-gordian-knot': 'https://threepanel.com/t/cube-drone/18/91',
        'comics/c/tone-deaf': 'https://threepanel.com/t/cube-drone/18/147',
        'comics/c/dont-prod-the-bear': 'https://threepanel.com/t/cube-drone/18/130',
        'comics/c/pep8-vs-v05': 'https://threepanel.com/t/cube-drone/18/114',
        'comics/c/severance-package': 'https://threepanel.com/t/cube-drone/18/129',
        'comics/c/some-like-it-hot': 'https://threepanel.com/t/cube-drone/18/117',
        'comics/c/yaoi': 'https://threepanel.com/t/cube-drone/18/128',
        'comics/c/1000-kg': 'https://threepanel.com/t/cube-drone/18/90',
        'comics/c/cyberpunk-2016': 'https://threepanel.com/t/cube-drone/18/148',
        'comics/c/cyberpunk-2015': 'https://threepanel.com/t/cube-drone/18/100',
        'comics/c/rfc-2324': 'https://threepanel.com/t/cube-drone/18/97',
        'comics/c/its-harder-in-a-distributed-environment': 'https://threepanel.com/t/cube-drone/18/96',
        'comics/c/variations-on-a-theme': 'https://threepanel.com/t/cube-drone/18/105',
        'comics/c/a-funny-thing-happened-on-the-way-to-the-forum': 'https://threepanel.com/t/cube-drone/18/134',
        'comics/c/keyboardio': 'https://threepanel.com/t/cube-drone/18/107',
        'comics/c/missing-the-point': 'https://threepanel.com/t/cube-drone/18/108',
        'comics/c/holy-war': 'https://threepanel.com/t/cube-drone/18/103',
    }


def pattern_url(pattern):
    return "https://s3-us-west-2.amazonaws.com/subtle-patterns/{pattern}.png".format(pattern=pattern)

def random_pattern(pattern_type=None):
    if pattern_type == 'light':
        return pattern_url(random.choice(LIGHT_PATTERNS))
    if pattern_type == 'dark':
        return pattern_url(random.choice(DARK_PATTERNS))
    else:
        return pattern_url(random.choice(PATTERNS))


class LocalEnvironment:
    """
    A wrapper around jinja2's "Environment" that does most of the setup
    """

    def __init__(self, path):
        self.target_path = os.path.join(path, 'generated')
        self.template_path = os.path.join(path, 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_path), autoescape=select_autoescape(['html', 'xml']))


    def render_template(self, template, opts, filename):
        """
        Shortcut function: render the template at /templates/<template>
        Using the dict of options in <opts>
        And then drop it into /generated/<filename>
        """

        template_obj = self.env.get_template(template)

        rendered_template = template_obj.render(opts)

        path = os.path.join(self.target_path, filename)

        print("{template_path}/{template} \n\t ==> {path}".format(template_path=self.template_path, template=template, path=path))

        with open(path, 'w') as f:
            f.write(rendered_template)


@task(optional=['path'])
def all(ctx, path=None):
    generate(ctx, path=path)
    generate_nginx_config(ctx, path=path)


@task(optional=['feed_url', 'path'])
def generate(ctx, feed_url=None, path=None):
    """
    Generate cube-drone.com from an RSS file
    """

    if not feed_url:
        feed_url = FEED_URL

    if not path:
        path = PATH

    local_env = LocalEnvironment(path)

    r = feedparser.parse(feed_url)

    feed = r.feed
    feed['favicon'] = "https://d24ju8re1w4x9e.cloudfront.net/original/2X/e/e4616b104f34924e0631cedf6e7fbf5ee523125e.png"
    feed['subtitle'] = "Comics about Code"
    feed['entries'] = r.entries
    feed['year'] = datetime.datetime.now().year

    print(json.dumps(feed, indent=4))

    style_opts = {}
    style_opts['bg_pattern_url'] = random_pattern(pattern_type='dark')
    style_opts['fg_pattern_url'] = random_pattern(pattern_type='light')

    local_env.render_template(template='index.j2', opts=feed, filename='index.html')
    local_env.render_template(template='style.j2', opts=style_opts, filename='style.css')


@task(optional=['path'])
def generate_nginx_config(ctx, path=None):
    """
    Generate the entire nginx configuration for this service.
    """
    if not path:
        path = PATH

    local_env = LocalEnvironment(path)

    nginx_opts = {}
    nginx_opts['papertrail_host'] = PAPERTRAIL_HOST
    nginx_opts['papertrail_port'] = PAPERTRAIL_PORT
    nginx_opts['rewrite_rules'] = REWRITE_RULES
    nginx_opts['sendfile'] = 'off'

    nginx_filename = os.path.join(path, 'nginx.conf')
    nginx_site_filename = os.path.join(path, 'default')

    local_env.render_template(template='nginx.j2', opts=nginx_opts, filename='nginx.conf')
    local_env.render_template(template='nginx_site.j2', opts=nginx_opts, filename='default')
