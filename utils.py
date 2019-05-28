import json
from multiprocessing import Process, Pool

from scrapers import CountriesScraper, LinksScraper, RegionsScraper, Region
from time import time, sleep
from os import path, mkdir
#country name and config
def process_country(country, config):

    links_filename = config['data_folder_name'] + '/links/{}.json'.format(country.name)

    if path.isfile(links_filename):
        print('You seem to have the links for {}'.format(country.name))
        
        with open(links_filename, mode='r', encoding='utf-8') as country_file:
            regions_dict = json.load(country_file)
            regions = [Region(*r.values(), None, None, None) for r in regions_dict]
            country_file.close()
    else:
        links_scraper = LinksScraper(country)
        data = links_scraper.get_links()
        regions = data

        with open(links_filename, mode='w', encoding='utf-8', newline='') as country_file:
            data_dict = [region.as_dict() for region in data]
            json.dump(data_dict, country_file)
            country_file.close()
        print('  > Links for {} have been written to {}'.format(country.name, links_filename))
    
    regions_filename = config['data_folder_name'] + '/regions' + '/{}.csv'.format(country.name)

    if path.isfile(regions_filename):
        print('You seem to have the region data for {}'.format(country.name))
    else:
        regions_scraper = RegionsScraper(regions)
        country_regions = regions_scraper.get_regions()

        with open(regions_filename, mode='w', encoding='utf-8', newline='') as regions_file:
            for region in country_regions:
                regions_file.write(region)
            regions_file.close()
        print('  > Regions for {} have been written to {}'.format(country.name, regions_filename))


def run_scraper_with(config):

    if not path.isdir(config['data_folder_name']):
        mkdir(config['data_folder_name'])
        mkdir(config['data_folder_name']+'/regions')
        mkdir(config['data_folder_name']+'/links')

    countries_scraper = CountriesScraper(config['base_url'])
    countries = countries_scraper.get_countries(config['countries'], config['number_of_countries'])

    start = time()

    pool = Pool(30)
    configs = [config for i in range(len(countries))]

    results = pool.starmap(process_country, zip(countries, configs))
    """
    for country in countries:
        results.append(pool.apply_async(process_country, (country, config)))
    """
    print(results)
    pool.close()

    stop = time()
    total_seconds = stop - start
    hours = int(total_seconds / 3600)
    minutes = int((total_seconds % 3600) / 60)
    seconds = int((total_seconds % 3600) % 60)
    print('total run time: {}h {}m {}s'.format(hours, minutes, seconds))

        #process = Process(target=process_country, args=(country, config))
        #process.start()
    
    