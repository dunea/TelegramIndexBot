import json

from app.core.settings import settings
from app.core.tme_scraper import TmeScraper

if __name__ == '__main__':
    scraper = TmeScraper(settings.SMARTDAILI_SCRAPER_TOKEN)
    s_result = scraper.get_tme_info("nuoyea")
    print(s_result)
