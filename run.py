from utils import run_scraper_with


if __name__ == '__main__':

    countries = [
      # 'Romania',
      'albania',
      'austria',
       'ukraine',
       'germany',
       'belgium',
       'denmark',
       'russia',
     
       




    ]

    config = {
        'base_url': 'http://postcode.info', # <---- DONT change this
        'data_folder_name': 'datanew',         # <---- DO change this to your liking
        'number_of_countries': 'all',       # <---- 'all' or a number (integer)
        'countries': countries
    }

    run_scraper_with(config)

