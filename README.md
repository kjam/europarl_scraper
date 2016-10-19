# europarl_scraper
A Python scrapy project for scraping data from [European Parliament's website](http://www.europarl.europa.eu/).


## Installation

    pip install -r requirements.txt

## Just give me the data!

It's on S3 in a public bucket! 
 
 * https://s3.eu-central-1.amazonaws.com/europarlspeeches/speech_urls.csv
 * https://s3.eu-central-1.amazonaws.com/europarlspeeches/speeches.csv
 * https://s3.eu-central-1.amazonaws.com/europarlspeeches/europarl_speech_text.txt (this is ONLY the speech text)
 * https://s3.eu-central-1.amazonaws.com/europarlspeeches/speakers.csv
 * https://s3.eu-central-1.amazonaws.com/europarlspeeches/debates.csv


## To run:

* First, grab the start urls. Run python get_urls.py

* Then, run any of the scrapers:

`scrapy crawl europarl_speeches -o data/speeches.csv`
`scrapy crawl europarl_debates -o data/debates.csv`
`scrapy crawl europarl_speakers -o data/speakers.csv`

## Notes

There are many TODO's for this still, so plz be patient.

* Figure out why not all members are in initial JSON
* Where are sources for this? https://github.com/eliflab/European-Parliament-Open-Data/blob/master/meps_full_list_with_twitter_accounts.csv
* How to divide work to speed up?

## Questions?

Feel free to reach out on Twitter or Freenode (@kjam).
