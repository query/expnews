#!/usr/bin/env python3

import cgi
from datetime import datetime, timedelta
import json
import math
import sys
import urllib.parse
import urllib.request

from jinja2 import Template


API_URL = 'https://api.npr.org/query?{}'
API_KEY = ''

TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>NPR Exponential News Lookback</title>
    <style>
        body {
            font-family: 'Verdana', sans-serif;
        }

        h1 {
            font-weight: normal;
        }

        section {
            padding-left: 20em;
            position: relative;
            margin: 1em 0;
        }

        section h1 {
            position: absolute;
            left: 0;
            top: 0;
            margin: 0;
        }

        section .subhead {
            position: absolute;
            left: 0;
            top: 2em;
            color: gray;
        }

        ul {
            margin: 0;
            padding: 0;
        }

        li {
            list-style: none;
        }
    </style>
</head>
<body>
    <h1>NPR Exponential News Lookback</h1>
    {% for date in timeline %}
        <section>
            <h1>
                <var>e</var><sup>{{ date.exponent }}</sup>
                {{ date.days_ago }}
            </h1>
            <div class="subhead"><time>{{ date.date }}</time></div>
            <ul>
                {% for story in date.stories %}
                    <li><a href="{{ story.url }}">{{ story.title }}</a></li>
                {% endfor %}
            </ul>
        </section>
    {% endfor %}
    <footer>
        <p>
            Powered by the <a href="http://www.npr.org/api/">NPR API</a>.
            The NPR Exponential News Lookback was created by
            <a href="http://alerante.net/">Roger Que</a>, and is not otherwise
            affiliated with NPR or any NPR member stations.
            <a href="https://github.com/query/expnews">Source code</a>.
        </p>
    </footer>
</body>
</html>
'''


def exponential_timeline_dates(num_entries=9):
    now = datetime.now()
    return [now - timedelta(days=math.exp(i)) for i in range(num_entries)]


def top_stories(date):
    qs = urllib.parse.urlencode({'apiKey': API_KEY,
                                 'id': 1002,  # "Home Page Top Stories"
                                 'date': date.date().isoformat(),
                                 'format': 'json'})
    with urllib.request.urlopen(API_URL.format(qs)) as f:
        charset = cgi.parse_header(f.info()['Content-Type'])[1]['charset']
        output = json.loads(f.read().decode(charset))
    stories = []
    for story in output['list']['story']:
        summary = {}
        summary['title'] = story['title']['$text']
        for link in story['link']:
            if link['type'] == 'html':
                summary['url'] = link['$text']
        stories.append(summary)
    return stories


def main():
    global API_KEY
    if len(sys.argv) != 2:
        print('usage: {} API_KEY'.format(sys.argv[0]), file=sys.stderr)
        return
    API_KEY = sys.argv[1]
    dates = exponential_timeline_dates()
    timeline = []
    for i, date in enumerate(dates):
        timeline.append({'exponent': i,
                         'days_ago': ('= 1 day ago' if i == 0 else
                                      '≈ {:.2f} days ago'.format(math.exp(i))),
                         'date': '{:%Y-%m-%d}'.format(date),
                         'stories': top_stories(date)})
    print(Template(TEMPLATE).render(timeline=timeline))


if __name__ == '__main__':
    main()
