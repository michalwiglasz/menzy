# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from bs4.element import Comment
import requests


base_url = 'http://www.kam.vutbr.cz/'
cantine_list_url = '?p=nabs'
cantine_hours_url = '?p=otdo'


def get_cantine_list():
    cantines = dict(get_info())
    for id, hours in get_hours():
        cantines[id]['hours'] = hours

    return cantines

    for cantine in cantines.itervalues():
        print ">>>", cantine['id'], cantine['name'].replace(u"–", "-")
        print cantine['menu_url']
        print cantine['img']
        print cantine['description'].replace(u"–", "-")
        print ', '.join(cantine['hours'].itervalues()).replace(u"–", "-")
        print
        print get_menu(cantine['menu_url'])


def get_info():
    response = requests.get(base_url + cantine_list_url)
    soup = BeautifulSoup(response.text)

    tags = soup.find_all('div', 'castclanku')
    for t in tags:
        cantine = dict(((s, None) for s in ['name', 'img', 'menu_url', 'id',
                                            'address', 'description',
                                            'hours']))
        t.h2.small.decompose()
        cantine['name'] = t.h2.get_text()
        cantine['img'] = base_url + t.img['src'] if t.img else None

        justobal = t.find('div', 'justobal')
        links = justobal.find_all('a')

        try:
            href = links[0]['href']
            cantine['menu_url'] = base_url + href
            cantine['id'] = int(href.split('=')[-1])
        except IndexError:
            continue

        addrScrapped = False
        descStarted = False
        description = []
        for string in justobal.strings:
            if not addrScrapped:
                cantine['address'] = string
                addrScrapped = True

            elif (descStarted
                  and string.parent.name not in ['img', 'script']
                  and not isinstance(string, Comment)):
                description.append(string)

            elif string[0] == ')':
                descStarted = True

        cantine['description'] = ''.join(description).strip()
        yield cantine['id'], cantine


def get_hours():
    response = requests.get(base_url + cantine_hours_url)
    soup = BeautifulSoup(response.text)
    content = soup.find('div', id='contentdiv')

    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    for row in content.table.find_all('tr'):
        if not row.td:
            # skip table header
            continue

        cantine = dict((s, {'from': [], 'to': [], 'text': []}) for s in days)

        id = int(row.a['href'].split('=')[-1])
        cells = list(row.find_all('td'))

        if (id and len(cells)):
            for i, day in enumerate(days):
                cell = cells[i - 2] if i > 3 else cells[1]

                divs = list(cell.find_all('div'))
                if len(divs):
                    for div in divs:
                        text = div.get_text()
                        _decrypt_hours(text, cantine, day)

                else:
                    text = cell.get_text()
                    _decrypt_hours(text, cantine, day)

            yield id, cantine


def _decrypt_hours(text, cantine, day):
    cantine[day]['text'].append(text)

    if u'–' in text:
        h_from, h_to = text.split(u'–', 1)
        cantine[day]['from'].append(int(h_from.split(':')[0]))
        cantine[day]['to'].append(int(h_to.split(':')[0]))


def get_cantine_menu(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    content = soup.find('div', id='contentdiv')

    menu = {
        'meals': [],
        'message': None,
    }

    types = {'H': 'main', 'P': 'soup', 'O': 'other'}

    if content.table:
        for row in soup.table.find_all('tr'):
            meal = dict((x, None) for x in ['type', 'weight', 'name',
                                            'price_student', 'price_employee',
                                            'price_other'])
            weight = row.find('td', 'levy').small
            meal['weight'] = get_weight(weight)
            weight.decompose()
            meal['type'] = types[row.find('td', 'levy').get_text().strip()]
            meal['name'] = list(row.find('td', 'levyjid').strings)[0].strip()
            meal['price_student'] = get_price(row.find('td', 'slcen1'))
            meal['price_employee'] = get_price(row.find('td', 'slcen2'))
            meal['price_other'] = get_price(row.find('td', 'slcen3'))
            menu['meals'].append(meal)

        msg = soup.table.find_previous_sibling('p')
        if msg:
            menu['message'] = msg.get_text().strip()

    else:
        if content.p:
            menu['message'] = content.p.get_text().strip()

    return menu


def get_weight(element):
    weight = element.get_text().strip()
    if weight:
        weight = int(weight[:-2])
    return weight


def get_price(element):
    return int(element.get_text().strip()[:-2])


if __name__ == '__main__':
    get_cantine_list()
