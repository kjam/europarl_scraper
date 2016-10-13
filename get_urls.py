from __future__ import print_function, unicode_literals
import requests
import pandas as pd
from time import sleep


def get_start_urls():
    """ populate start urls with full search json """
    resp = requests.post(
        'http://www.europarl.europa.eu/meps/en/json/newperformsearchjson.html')
    speaker_urls = ['http://www.europarl.europa.eu{}'.format(r.get('detailUrl'))
                    for r in resp.json().get('result')]
    all_speeches = []
    # want to merely test with a smaller set? uncomment below and comment out
    # matching line in for loop. It will give you only 90 speeches :)
    # next_page, index = True, 0
    for speaker in speaker_urls:
        next_page, index = True, 0
        url_split = speaker.split('/')[:-1]
        url_split.append('see_more.html')
        base_url = '/'.join(url_split)
        while next_page:
            resp, tries = None, 0
            while not resp and tries < 10:
                try:
                    resp = requests.get(base_url,
                                        params={'type': 'CRE', 'index': index})
                    if resp.json().get('nextIndex') == -1 or resp.json().get('nextIndex') == index:
                        next_page = False
                    else:
                        index = resp.json().get('nextIndex')
                    all_speeches.extend([s.get('titleUrl') for s in
                                         resp.json().get('documentList')])
                    print('len all speeches: %d' % len(all_speeches))
                except Exception as e:
                    print(e)
                    print('error: with {} index {}'.format(base_url, index))
                    sleep(10)
                    tries += 1
    df = pd.DataFrame(all_speeches, columns=['url'])
    df = df.drop_duplicates()
    df.to_csv('data/speech_urls.csv')


if __name__ == '__main__':
    get_start_urls()
