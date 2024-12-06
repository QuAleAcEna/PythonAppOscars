
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import abort, render_template, Flask, request
import logging
import mydb as mydb
mydb.connect()


APP = Flask(__name__, template_folder='C:/Users/Dinis/Desktop/uni/base dados/projeto/app/mytemplates')

# Start page
@APP.route('/')
def index():
    stats = {}
    stats = mydb.execute('''
    SELECT
      (SELECT COUNT(*) FROM Films) as n_films,
      (SELECT COUNT(*) FROM Nominees) as n_nominees,
      (SELECT COUNT(*) FROM Categories) as n_categories,
      (SELECT COUNT(*) FROM Ceremonies) as n_ceremonies
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html', stats=stats)

# Films
@APP.route('/films/')
def list_films():
    films = mydb.execute(
      '''
      SELECT id, name
      FROM Films
      ORDER BY name
      ''').fetchall()
    return render_template('film-list.html', films=films)


@APP.route('/films/<int:id>/')
def get_film(id):
    # Get the film details
    film = mydb.execute('''
        SELECT id, name FROM Films WHERE id = ?
    ''', [id]).fetchone()

    if not film:
        abort(404, 'Film not found')

    # Get the actors for the film from the NominationFilms and Nominees tables
    actors = mydb.execute('''
        SELECT DISTINCT Nominees.id, Nominees.name
        FROM NominationFilms
        JOIN NominationEntities ON NominationFilms.nomination = NominationEntities.nomination
        JOIN Nominees ON NominationEntities.nominee = Nominees.id
        WHERE NominationFilms.film = ?
        ORDER BY Nominees.name
    ''', [id]).fetchall()

    # Get the nominations (awards) for the film
    nominations = mydb.execute('''
        SELECT Categories.name as category_name, Nominations.winner
        FROM Nominations
        JOIN Categories ON Nominations.category = Categories.id
        JOIN NominationFilms ON NominationFilms.nomination = Nominations.id
        WHERE NominationFilms.film = ?
    ''', [id]).fetchall()

    return render_template('film-detail.html', film=film, actors=actors, nominations=nominations)

@APP.route('/films/search', methods=['GET'])
def search_films():
    search_term = request.args.get('search_term', '')
    films = mydb.execute('''
        SELECT id, name FROM Films WHERE name LIKE ?
    ''', ['%' + search_term + '%']).fetchall()
    return render_template('film-list.html', films=films)



# Nominees
@APP.route('/nominees/')
def list_nominees():
    nominees = mydb.execute('''
        SELECT id, name FROM Nominees
        GROUP BY name  
        ORDER BY name
    ''').fetchall()
    return render_template('nominee-list.html', nominees=nominees)



@APP.route('/nominees/<int:nominee_id>/')
def get_nominee(nominee_id):
    # Get the nominee's details (name, etc.)
    nominee = mydb.execute('''
        SELECT id, name FROM Nominees WHERE id = ?
    ''', [nominee_id]).fetchone()

    if not nominee:
        abort(404, 'Nominee not found')

    # Get the nominee's nominations history (with winner status and year)
    nominations = mydb.execute('''
        SELECT Categories.name AS category, Nominations.winner, Ceremonies.year
        FROM NominationEntities
        JOIN Nominations ON NominationEntities.nomination = Nominations.id
        JOIN Categories ON Nominations.category = Categories.id
        JOIN Ceremonies ON Nominations.cerimony = Ceremonies.cerimony
        WHERE NominationEntities.nominee = ?
        ORDER BY Ceremonies.year
    ''', [nominee_id]).fetchall()

    return render_template('nominee-detail.html', nominee=nominee, nominations=nominations)


@APP.route('/nominees/search', methods=['GET'])
def search_nominees():
    search_term = request.args.get('search_term', '')
    nominees = mydb.execute('''
        SELECT id, name FROM Nominees WHERE name LIKE ?
        GROUP BY name  -- Ensures unique results
        ORDER BY name
    ''', ['%' + search_term + '%']).fetchall()
    return render_template('nominee-list.html', nominees=nominees)





@APP.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('search_term', '')
    
    # Search in Films table
    films = mydb.execute('''
        SELECT id, name FROM Films WHERE name LIKE ?
    ''', ['%' + search_term + '%']).fetchall()
    
    # Search in Nominees (actors)
    actors = mydb.execute('''
        SELECT id, name FROM Nominees WHERE name LIKE ?
    ''', ['%' + search_term + '%']).fetchall()
    
    # Search in Nominations (awards)
    nominations = mydb.execute('''
        SELECT id, name FROM Nominations WHERE name LIKE ?
    ''', ['%' + search_term + '%']).fetchall()
    
    # Search in Ceremonies
    ceremonies = mydb.execute('''
        SELECT cerimony, year FROM Ceremonies WHERE year LIKE ?
    ''', ['%' + search_term + '%']).fetchall()
    
    # Pass search results to the template
    return render_template('search_results.html', search_term=search_term, films=films, actors=actors, nominations=nominations, ceremonies=ceremonies)

# Route for Categories
@APP.route('/categories/')
def list_categories():
    categories = mydb.execute('''
        SELECT id, name FROM Categories ORDER BY name
    ''').fetchall()
    return render_template('category-list.html', categories=categories)

# Route for Ceremonies
@APP.route('/ceremonies/')
def list_ceremonies():
    # Extract the first part of the year for sorting purposes
    ceremonies = mydb.execute('''
        SELECT cerimony, year FROM Ceremonies
        ORDER BY CAST(substr(year, 1, 4) AS INTEGER)
    ''').fetchall()
    return render_template('ceremony-list.html', ceremonies=ceremonies)

@APP.route('/ceremonies/<int:ceremony_id>/')
def get_ceremony(ceremony_id):
    # Get the details of the selected ceremony
    ceremony = mydb.execute('''
        SELECT cerimony, year FROM Ceremonies WHERE cerimony = ?
    ''', [ceremony_id]).fetchone()

    if not ceremony:
        abort(404, 'Ceremony not found')

    # Get the categories for the selected ceremony
    categories = mydb.execute('''
        SELECT Categories.id, Categories.name
        FROM Nominations
        JOIN Categories ON Nominations.category = Categories.id
        WHERE Nominations.cerimony = ?
        GROUP BY Categories.id
        ORDER BY Categories.name
    ''', [ceremony_id]).fetchall()

    # Get the nominees and the winners for each category
    category_details = []
    for category in categories:
        # Print out to debug the structure of the category row
        print(category)

        nominees = mydb.execute('''
            SELECT Nominees.name, Nominations.winner
            FROM NominationEntities
            JOIN Nominees ON NominationEntities.nominee = Nominees.id
            JOIN Nominations ON NominationEntities.nomination = Nominations.id
            WHERE Nominations.category = ? AND Nominations.cerimony = ?
        ''', [category['id'], ceremony_id]).fetchall()

        category_details.append({
            'category': category,
            'nominees': nominees
        })

    return render_template('ceremony-detail.html', ceremony=ceremony, category_details=category_details)
