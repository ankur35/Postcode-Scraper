import requests
from bs4 import BeautifulSoup
from time import time


class Country(object):

    def __init__(self, name, alpha2, url):

        self.name = name
        self.alpha2 = alpha2
        self.url = url



class Page(object):

    def __init__(self, baseurl, url):

        self.baseurl = baseurl
        self.url = url



class Region(object):

    def __init__(self, name, url, country_name, country_alpha2, postcode, longitude, latitude):
        self.name = name
        self.url = url
        self.country_name = country_name
        self.country_alpha2 = country_alpha2
        self.postcode = postcode
        self.longitude = longitude
        self.latitude = latitude


    def as_dict(self):
        if self.postcode is None or self.longitude is None or self.latitude is None:
            return {
                'name': self.name,
                'url': self.url,
                'country_name': self.country_name,
                'country_alpha2': self.country_alpha2
            }
        
        return {
            'name': self.name,
            'url': self.url,
            'country_name': self.country_name,
            'country_alpha2': self.country_alpha2,
            'postcode': self.postcode,
            'longitude': self.longitude,
            'latitude': self.latitude
        }

    def as_csv_rows(self):

        if self.postcode is None or self.longitude is None or self.latitude is None:
            return ['\t'.join([
                self.country_alpha2,
                self.name,
            ]) + '\n']
        
        rows = []

        for postcode in self.postcode.split(','):
            rows.append('\t'.join([
                self.country_alpha2,
                self.name,
                postcode,
                self.latitude,
                self.longitude]) + '\n')

        return rows


class CountriesScraper(object):

    def __init__(self, url):
        self.url = url
    
    def get_countries(self, country_names, number_of_countries):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        countries = self.extract_countries(soup)
        
        return self.filter_countries(countries, country_names, number_of_countries)


    def extract_countries(self, soup):
        countries = []

        container = soup.find(**{'class': 'content'}).find(**{'class': 'cnt'})
        links = container.find_all('a')

        for link in links:
            url = link['href']
            name = link.text.split('=')[-1].split('(')[0].strip()
            alpha2 = link.text.split('=')[0].strip()
            country = Country(name, alpha2, url)
            countries.append(country)

        return countries


    def filter_countries(self, countries, country_names, number_of_countries):
        country_names = [country_name.lower() for country_name in country_names]

        result = []

        for country in countries:
            if country.name.lower() in country_names:
                result.append(country)

        if number_of_countries == 'all':
            return result
        if isinstance(number_of_countries, int):
            return result[:number_of_countries]
        elif isinstance(number_of_countries, list):
            return result[number_of_countries[0]:number_of_countries[1]]



class LinksScraper(object):

    def __init__(self, country):
        self.country = country


    def get_links(self):
        response =  requests.get(self.country.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        country_page = Page(self.country.url, self.country.url)

        regions = []
        seen = []
        pages = [country_page]
        count = 0
        start = time()

        for page in pages:
            if page.url in seen:
                continue

            soup = BeautifulSoup(requests.get(page.url).text, 'html.parser')
            seen.append(page.url)

            if self.is_category_page(soup):
                extracted_pages = self.extract_pages(page, soup)
                pages.extend(extracted_pages)
                count += 1
            else:
                regions.extend(self.extract_regions(page, soup))
                count += 1
            
            if count % 100 == 0:
                stopi = time()
                total_seconds = stopi-start
                seconds = int((total_seconds % 3600) % 60)
                minutes = int((total_seconds % 3600) / 60)
                hours = int(total_seconds/3600)
                print('  > Scraped {0} link pages in {1}h {2}m {3}s for {4}'.format(count, hours, minutes, seconds, self.country.name))

        stop = time()
        total_seconds = stop-start
        seconds = int((total_seconds % 3600) % 60)
        minutes = int((total_seconds % 3600) / 60)
        hours = int(total_seconds/3600)

        print('  > Scraped {0} link pages in {1}h {2}m {3}s for {4}'.format(count, hours, minutes, seconds, self.country.name))
        return regions


    def is_category_page(self, soup):
        button_container = soup.find(**{'class': 'letterbutton'})
        page_title = soup.find(**{'class': 'content'}).find('h3')

        if page_title is not None and page_title.text == 'Select state (or region):':
            return True
        elif button_container is not None:
            return True
        else:
            return False


    def extract_pages(self, page, soup):
        button_container = soup.find(**{'class': 'letterbutton'})

        pages = []

        if button_container is not None:
            links = button_container.find_all('a')

            for link in links:
                url = link['href']
                new_page = Page(page.baseurl, page.baseurl + url)
                pages.append(new_page)
        else:
            container = soup.find(**{'class': 'content'}).find(**{'class': 'cnt'})
            links = container.find_all('a')

            for link in links:
                url = link['href']
                new_page = Page(page.baseurl+url, page.baseurl+url)
                pages.append(new_page)

        return pages


    def extract_regions(self, page, soup):
        container = soup.find(**{'class': 'content'}).find(**{'class': 'cnt'})
        links = container.find_all('a')

        regions = []

        for link in links:
            url = link['href']
            region_name = link.text.split('(')[0].strip()
            region = Region(region_name, page.baseurl + url, self.country.name, self.country.alpha2, None, None, None)
            regions.append(region)

        return regions


#takeback html data from links
class RegionsScraper(object):

    def __init__(self, regions):
        self.regions = regions

    
    def get_regions(self):
        scraped_pages = 0

        start1 = time()
        for i, region in enumerate(self.regions):
            response = requests.get(region.url)
            soup = BeautifulSoup(response.text, 'html.parser')

            self.extract_region_data(region, soup)
            scraped_pages += 1

            if scraped_pages % 100 == 0:
                stop = time()
                total_seconds = stop-start1
                seconds = int((total_seconds % 3600) % 60)
                minutes = int((total_seconds % 3600) / 60)
                hours = int(total_seconds/3600)
                print('  > Scraped {0} region pages in {1}h {2}m {3}s for {4}'.format(scraped_pages, hours, minutes, seconds, region.country_name))

        stop1 = time()
        total_seconds = stop1-start1
        seconds = int((total_seconds % 3600) % 60)
        minutes = int((total_seconds % 3600) / 60)
        hours = int(total_seconds/3600)
        print('  > Scraped {0} region pages (complete) in {1}h {2}m {3}s'.format(scraped_pages, hours, minutes, seconds))

        rows = []

        for region in self.regions:
            if region.longitude is None or region.latitude is None or len(region.name.strip()) == 0:
                continue
            rows.extend(region.as_csv_rows())
        
        return rows


    def extract_region_data(self, region, soup):
        container = soup.find(**{'class': 'content'}).find(**{'class': 'cnt'})
        datarow = container.text.split('>>')[-1]
        if 'GPS coordinates:' not in datarow:
            coords = [None, None]
        else:
            coords = datarow.split(':')[-1].split('\n')[0].split(',')
        postcodes = []

        for link in container.find_all('a'):
            if link.text.strip() == 'this map' or link.text.strip() == 'Google':
                continue
            postcodes.append(link.text.strip())
        
        postcode = ','.join(postcodes)
        region.postcode = postcode
        region.longitude = coords[0] if coords[0] is None else coords[0].strip()

        if len(coords) > 1:
            region.latitude = coords[1] if coords[1] is None else coords[1].strip()
        else:
            region.latitude = None
