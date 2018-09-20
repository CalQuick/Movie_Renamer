# Scans a directory of films. Queries filenames with IMDB and renames bad filenames correctly.
# Creates a database of films with info on their rating, actors, genre etc.
# Gives the option to narrow down a film and open containing folder.

import os
import re
import shelve
import requests, bs4, webbrowser

current_dir = os.getcwd()
shelf_file = shelve.open(current_dir + '\\movie_data')

def directory_set():
    # User inputs directory string, and function changes directory to that folder if it is found.
    # repeat = True
    while True:

        try:    # First checks shelf_file for an existing directory
            print('Copy and paste the directory where all films are stored. Currently set at ' + shelf_file['directory'])
        except KeyError:    # If no directory is found, then returns different message.
            print('Copy and paste the directory where all films are stored.')
            directory = input()
        else:
            print('If you don\'t wish to change, press enter. Otherwise paste new path and enter')
            ans = input()
            if ans == '':   # Keep directory the same as shelf_file
                directory = shelf_file['directory']
            else:
                directory = ans

        try:
            os.chdir(directory)
        except FileNotFoundError:
            print('Unable to find that directory. Please try again.')
        except OSError:
            print('Nothing entered')
        else:
            print('Success! The directory has been set to: ' + os.getcwd())
            print()
            shelf_file['directory'] = directory
            break

def directory_scan(directory):
    movies = []
    print('Looking up films...')
    for folder, subfolder, files in os.walk(directory):

        for file in files:
            mov1 = Movie.from_imdb(file, folder)
            try:
                # File in new directory of films e.g. disney films - or base directory
                if (len(os.listdir(folder)) > 1 and folder != shelf_file['directory']) or (folder == shelf_file['directory']):
                    # TODO: run funciton based on name being filename. Don't rename folder.
                    mov1.rename_file()
                # File in normal directory. Rename folder afterwards
                else:
                    # TODO: run function which includes folder rename afterwards.
                    mov1.rename_file(True)
            except AttributeError:
                pass
    print('End of lookup')
    print()

def delete_empties(directory):
    for folder, subfolder, files in os.walk(directory):
        try:
            os.rmdir(folder)
        except:
            pass

class Movie:
    def __init__(self, title, year, genre, rating, filename, location, ext):
        self.title = title
        self.year = year
        self.genre = genre
        self.rating = rating
        self.filename = filename
        self.location = location
        self.ext = ext

    @classmethod
    def from_imdb(cls, filename, location):
        # Takes filename, and searches IMDB to return movie attributes #
        filename = filename    # sets starting filename (before rename)
        location = location    # sets starting location
        name, ext = os.path.splitext(filename)
        name = fix_filename(name)
        # Searches IMDB based on filename input. Returns film information.
        res = requests.get(r'https://www.imdb.com/find?ref_=nv_sr_fn&q=' + '+'.join(name.split()))
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html5lib")
        try:
            answer = soup.select('.result_text > a')[0].get('href')
        except IndexError as e:
            name = fix_filename(name)
            res = requests.get(r'https://www.imdb.com/find?ref_=nv_sr_fn&q=' + '+'.join(name.split()))
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.text, "html5lib")
            try:
                answer = soup.select('.result_text > a')[0].get('href')
            except IndexError as e:
                print('Unable to find {} due to {}'.format(name, e))
        else:
            # Opens first result
            res = requests.get(r'https://www.imdb.com' + answer)
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.text, "html5lib")
            year = int(soup.select('#titleYear a')[0].text)  # returns film year
            title = soup.select('.title_wrapper > h1')[0].text  # title and year
            title = title.rstrip()[:-7]  # removes date from title
            rating = soup.select(
                '#title-overview-widget > div.vital > div.title_block > div > div.ratings_wrapper > div.imdbRating > div.ratingValue > strong > span')[
                0].text
            genre = soup.select('.subtext .itemprop')[0].text  # gets first genre
            return cls(title, year, genre, rating, filename, location, ext)

    def rename_file(self, rename_folder=False):
        # rename file first
        old_filename_path = self.location + '\\' + self.filename
        new_foldername = '{} ({}) - {} - Rating {}'.format(self.title, self.year, self.genre, self.rating)
        new_folder_path = shelf_file['directory'] + '\\' + new_foldername
        new_filename = '{} ({})'.format(self.title, self.year)
        new_filename_path = new_folder_path + '\\' + new_filename + self.ext

        print('Renaming ' + self.title)

        # Moves file out of base directory if in there
        if self.location == shelf_file['directory']:
            os.makedirs(new_folder_path, exist_ok=True)
            os.rename(old_filename_path, new_filename_path)
        # rename folder (optional)
        elif rename_folder:
            print('Renaming folder to ' + new_folder_path)
            os.rename(self.location, new_folder_path)
            old_filename_path = new_folder_path + '\\' + self.filename
            os.rename(old_filename_path, new_filename_path)
        else:
            os.rename(old_filename_path, self.location + '\\' + new_filename + self.ext)

def fix_filename(file):
    # First tries to find a year
    regex = re.compile('.+\d\d\d\d\)?') # Matches a string with anything followed by 4 numbers and one or none ')'
    try:
        return regex.search(file).group()
    # If no year found, just takes the first 4 words as search terms
    except AttributeError:
        return ' '.join(file.split('.')[:4])

    # TODO - STRIP NAME OF RIPPERS DETAILS
    # Finding Nemo 2003 iNTERNAL DVDRip XviD-8BaLLRiPS
    return newname


directory_set()
directory_scan(shelf_file['directory'])
delete_empties(shelf_file['directory'])



# shelf_file.close()
