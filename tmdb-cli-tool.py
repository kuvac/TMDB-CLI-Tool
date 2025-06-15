import argparse
import requests
from datetime import datetime


warning_color = '\033[91m' # the color the warning messages will be (currently red)
program_color = '\033[93m' # the color the printed results will be in (currently yellow)
reset_color = '\033[0m' # resets the terminal color and styles

API_KEY = '91b5c90ea62bb47c152e730515469a5a'
params={
    'api_key': API_KEY
    }

def format_tmdb(date):
    if isinstance(date, datetime):
        return date.strftime('%Y-%m-%d')

    if isinstance(date, str):
        date = date.strip()
        try:
            datetime.strptime(date, '%Y-%m-%d')
            return date
        except ValueError:
            return None
    
    return None

def get_movies(url):
    response = requests.get(url, params)

    if response.status_code != 200:
        try:
            data = response.json()
        except ValueError:
            data = {}
        if response.status_code == 401:
            print(f"{warning_color}Authentication failed.{reset_color}")
        elif response.status_code == 429:
            print(f"{warning_color}Rate limit exceeded. Please try again later.{reset_color}")
        elif response.status_code >= 500:
            print(f'{warning_color}Server error on TMDB. Please try again later.{reset_color}')
        else:
            print(f"{warning_color}Error {data.get('status_code', response.status_code)}: {data.get('status_message', 'Unknown error')}{reset_color}")
        return
    else:
        data = response.json()
        movies = data.get('results', [])

        for movie in movies:
            print(f"{program_color}{movie['title'][:30]:<30}    Rating: {movie['vote_average']:.2f}   Release date:  {movie['release_date']}")
        print(f'{reset_color}')


def main():
    parser = argparse.ArgumentParser(description='Fetch a movie list')

    parser.add_argument('--type', help='Type of the movies: playing/popular/top/upcoming', choices=['playing', 'popular', 'top', 'upcoming'])
    parser.add_argument('--start_date', help='Filter movies based on a release date')
    parser.add_argument('--end_date', help='Filter movies based on a release date')

    args=parser.parse_args()

    today = datetime.today()
    min_date = "1900-01-01"
    max_date = format_tmdb(today)

    if args.start_date:
        formated_date = format_tmdb(args.start_date)
        if formated_date:
            min_date = formated_date
        else:
            print(f'{warning_color}Invalid start date format. Use YYYY-MM-DD.{reset_color}')
            return
    if args.end_date:
        formated_date = format_tmdb(args.end_date)
        if formated_date:
            max_date = formated_date
        else:
            print(f'{warning_color}Invalid end date format. Use YYYY-MM-DD.{reset_color}')
            return
    
    if min_date > max_date:
        print(f'{warning_color}Start date must be before end date.{reset_color}')
        return

    tmdb_api = {
        'playing': f'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&with_release_type=2|3&release_date.gte={min_date}&release_date.lte={max_date}',
        'popular': 'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc',
        'top': 'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=vote_average.desc&without_genres=99,10755&vote_count.gte=200',
        'upcoming': f'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&with_release_type=2|3&release_date.gte={min_date}&release_date.lte={max_date}'
    }

    movie_type = args.type or 'popular'
    get_movies(tmdb_api[movie_type])


if __name__ == '__main__':
    main()

