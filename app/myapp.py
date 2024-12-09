
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import abort, render_template, Flask, request
import logging
import mydb as mydb
mydb.connect()


APP = Flask(__name__, template_folder='mytemplates')

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
    most_film_oscars=mydb.execute('''
        SELECT 
            f.name,
            COUNT(f.id) AS oscars
        FROM 
            films f 
            JOIN nominations n ON n.film = f.id
        WHERE 
            n.winner = 1
        GROUP BY 
            f.id, f.name
        HAVING 
            COUNT(f.id) = (
                SELECT 
                    MAX(oscars_count)
                FROM (
                    SELECT 
                        COUNT(f.id) AS oscars_count
                    FROM 
                        films f
                        JOIN nominations n ON n.film = f.id
                    WHERE 
                        n.winner = 1
                    GROUP BY 
                        f.id
                ) max_oscars
            )
        ORDER BY 
            oscars DESC;

                                        ''').fetchall()
    most_nominations_films=mydb.execute('''
        select
            f.name as film,
            count(n.id) as nominations
        from 
            films f join nominations n on f.id=n.film
        group by
            f.id,f.name
        order by 
            nominations desc
        limit 10;
    ''').fetchall()
    
    most_awarded_person = mydb.execute('''
        SELECT n.name, COUNT(ne.nomination) AS oscars
        FROM Nominees n
        JOIN NominationEntities ne ON n.id = ne.nominee
        JOIN Nominations no ON ne.nomination = no.id
        WHERE no.winner = 1 AND n.percomp = 'person'
        GROUP BY n.name
        ORDER BY oscars DESC
        LIMIT 1;
    ''').fetchone()

    
    most_awarded_company = mydb.execute('''
        SELECT n.name, COUNT(ne.nomination) AS oscars
        FROM Nominees n
        JOIN NominationEntities ne ON n.id = ne.nominee
        JOIN Nominations no ON ne.nomination = no.id
        WHERE no.winner = 1 AND n.percomp = 'company'
        GROUP BY n.name
        ORDER BY oscars DESC
        LIMIT 1;
    ''').fetchone()
    multinom=mydb.execute('''
     select distinct
         c.year,
         cat.original_name as category,
            nom.name as nominee,
            f.name as film
            
        from  nominations nom
                join films f on f.id=nom.film join ceremonies c on c.ceremony=nom.ceremony
             join categories cat on cat.id=nom.category
        where 
            nom.multifilm_nomination=1;
                          ''').fetchall()

    return render_template('index.html', stats=stats,  most_film_oscars=most_film_oscars,most_nominations_films=most_nominations_films, most_awarded_person=most_awarded_person, most_awarded_company=most_awarded_company,multinom=multinom)

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
        SELECT id, name 
        FROM Films 
        WHERE id = ?
    ''', [id]).fetchone()

    if not film:
        abort(404, 'Film not found')

    # Get the nominations (awards) for the film
    nominations = mydb.execute('''
        SELECT 
            Categories.name as category_name, 
            Nominations.winner,
            Nominations.name,
            Nominations.id,
            c.year
        FROM Nominations
        JOIN Categories ON Nominations.category = Categories.id join ceremonies c on c.ceremony=nominations.ceremony
        WHERE Nominations.film = ?
    ''', [id]).fetchall()

    # Calculate the total Oscars (where winner = 1)
    total_oscars = mydb.execute('''
        SELECT COUNT(*) AS total
        FROM Nominations
        WHERE film = ? AND winner = 1
    ''', [id]).fetchone()['total']  # Extract the total count

    # Pass nominations as a dictionary with total
    nominations_data = {
        'list': nominations,
        'total': total_oscars  # Total is passed directly as an integer
    }

    return render_template('film-detail.html', film=film, nominations=nominations_data)


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
        SELECT Categories.name AS category, Nominations.winner, Ceremonies.year, f.name as film
        FROM NominationEntities
        JOIN Nominations ON NominationEntities.nomination = Nominations.id
        JOIN Categories ON Nominations.category = Categories.id
        JOIN Ceremonies ON Nominations.ceremony = Ceremonies.ceremony
        left join films f on f.id=nominations.film
        WHERE NominationEntities.nominee = ?
        ORDER BY Ceremonies.year
    ''', [nominee_id]).fetchall()

    return render_template('nominee-detail.html', nominee=nominee, nominations=nominations)


@APP.route('/nominees/search', methods=['GET'])
def search_nominees():
    search_term = request.args.get('search_term', '').strip()
    print(f"Search Term: {search_term}")  # Debugging
    nominees = mydb.execute('''
        SELECT id, name FROM Nominees WHERE name LIKE ?
        GROUP BY name
        ORDER BY name
    ''', ['%' + search_term + '%']).fetchall()
    print(f"Nominees: {nominees}")  # Debugging
    return render_template('nominee-list.html', nominees=nominees, search_term=search_term)

# Route for Categories
@APP.route('/categories/')
def list_categories():
    categories = mydb.execute('''
        SELECT id, name FROM Categories ORDER BY name
    ''').fetchall()
    return render_template('category-list.html', categories=categories)

@APP.route('/categories/search', methods=['GET'])
def search_categories():
    search_term = request.args.get('search_term', '').strip()
    print(f"Search Term: {search_term}")  # Debugging
    categories = mydb.execute('''
        SELECT id, name FROM categories WHERE name LIKE ?
        ORDER BY name
    ''', ['%' + search_term + '%']).fetchall()
    print(f"Categories: {categories}")  # Debugging
    return render_template('category-list.html', categories=categories, search_term=search_term)

# Route for Ceremonies
@APP.route('/ceremonies/')
def list_ceremonies():
    # Extract the first part of the year for sorting purposes
    ceremonies = mydb.execute('''
        SELECT ceremony, year FROM Ceremonies
        ORDER BY CAST(substr(year, 1, 4) AS INTEGER)
    ''').fetchall()
    return render_template('ceremony-list.html', ceremonies=ceremonies)

@APP.route('/ceremonies/<int:ceremony_id>/')
def get_ceremony(ceremony_id):
    # Get the details of the selected ceremony
    ceremony = mydb.execute('''
        SELECT ceremony, year FROM Ceremonies WHERE ceremony = ?
    ''', [ceremony_id]).fetchone()

    if not ceremony:
        abort(404, 'Ceremony not found')

    # Get the categories for the selected ceremony
    categories = mydb.execute('''
        SELECT Categories.id, Categories.name
        FROM Nominations
        JOIN Categories ON Nominations.category = Categories.id
        WHERE Nominations.ceremony = ?
        GROUP BY Categories.id
        ORDER BY Categories.name
    ''', [ceremony_id]).fetchall()

    # Get the nominations for each category
    category_details = []
    for category in categories:
        nominations = mydb.execute('''
            SELECT 
                Nominations.id AS nomination_id, 
                Nominations.name AS nomination_name, 
                Nominations.winner
            FROM Nominations
            WHERE Nominations.category = ? AND Nominations.ceremony = ?
        ''', [category['id'], ceremony_id]).fetchall()

        category_details.append({
            'category': category,
            'nominations': nominations
        })

    return render_template('ceremony-detail.html', ceremony=ceremony, category_details=category_details)

@APP.route('/nominations/<int:nomination_id>/')
def get_nomination_detail(nomination_id):
    # Fetch the nomination details by ID
    result = mydb.execute('''
        SELECT 
            nm.id AS nominee_id,
            nm.name AS name, 
            f.id AS film_id,
            f.name AS film,
            n.detail,
            n.note,
            n.citation
        FROM 
            nominees nm 
            JOIN nominationentities e ON nm.id = e.nominee
            JOIN nominations n ON n.id = e.nomination  
            LEFT JOIN films f ON n.film = f.id
        WHERE n.id = ?
    ''', [nomination_id]).fetchall()

    if not result:
        result = []

    nominees = [{
        'id': row['nominee_id'],
        'name': row['name'],
        'detail': row['detail'],
        'note': row['note'],
        'citation': row['citation']
    } for row in result]

    film_name = result[0]['film'] if result else None  # Get the film name
    film_id = result[0]['film_id'] if result else None
    # Render the nomination-detail template with the nomination data
    return render_template(
        'nomination-detail.html', 
        nominees=nominees, 
        film_id=film_id, 
        film_name=film_name
    )




@APP.route('/search_winner', methods=['GET', 'POST'])
def search_winner():
    if request.method == 'POST':
        # Normalize inputs to handle case insensitivity
        category = request.form.get('category', '').strip().lower()
        year_input = request.form.get('year', '').strip()

        # Handle empty inputs
        if not category or not year_input:
            return render_template('winner-result.html', error="Both category and year are required!")

        
            # Query the winner, handling both full year and range formats
        result = mydb.execute('''
                SELECT 
                    c.name AS category,
                    c.original_name as ogcategory,
                    cer.year,
                    nom.name AS winner,
                    nom.id as nomination_id
                FROM Nominations nom
                JOIN Categories c ON nom.category = c.id
                JOIN Ceremonies cer ON nom.ceremony = cer.ceremony
                WHERE (LOWER(c.name) = ? or lower(c.original_name)=?)
                    AND (
                      cer.year = cast(? as integer) 
                    or (cer.year != cast(? as integer)
                              
                        and CAST(SUBSTR(cer.year, 6, 7) AS INTEGER)  = cast(substr(?,3,4) as integer))
                )
                  AND nom.winner = 1;
            ''', [category,category, year_input, year_input,year_input]).fetchone()

        if result:
                return render_template('winner-result.html', result=result)
        else:
                return render_template('winner-result.html', error="No winner found for this category and year.")
        

    # Render the search form
    return render_template('winner-search.html')

@APP.route('/search_most_awarded', methods=['GET', 'POST'])
def search_most_awarded():
    if request.method == 'POST':
        year = request.form.get('year', '').strip()

        # Validate the input
        if not year.isdigit():
            return render_template('most-awarded-result.html', error="Please enter a valid year, between 1928 and 2023.")

        # Query for the movie with the most Oscars in the given year
        result = mydb.execute('''
           WITH FilmAwards AS (
                SELECT f.name AS film_name, COUNT(n.id) AS total_oscars,f.id as film_id,cer.year
                FROM Nominations n
                JOIN Films f ON n.film = f.id
                JOIN Ceremonies cer ON n.ceremony = cer.ceremony
                WHERE n.winner = 1                     AND (
                      cer.year = cast(? as integer) 
                    or (cer.year != cast(? as integer)
                              
                        and CAST(SUBSTR(cer.year, 6, 7) AS INTEGER)  = cast(substr(?,3,4) as integer))
                )
                GROUP BY f.name
            )
            SELECT film_name, total_oscars, film_id,year
            FROM FilmAwards
            WHERE total_oscars = (SELECT MAX(total_oscars) FROM FilmAwards)
            ORDER BY total_oscars DESC;
        ''', [year,year,year]).fetchall()

        if result:
            return render_template('most-awarded-result.html', year=year, result=result)
        else:
            return render_template('most-awarded-result.html', year=year, error="No data found, select a year between 1928 and 2023.")

    # Fetch the most awarded films by ceremony for display
    ceremony_query = '''
    WITH film_oscars AS (
        SELECT cer.year, f.name AS film_name, COUNT(n.id) AS total_oscars, f.id as film_id
        FROM Nominations n
        JOIN Films f ON n.film = f.id
        JOIN Ceremonies cer ON n.ceremony = cer.ceremony
        WHERE n.winner = 1
        GROUP BY cer.year, f.name
    ),
    max_oscars AS (
        SELECT year, MAX(total_oscars) AS max_oscars
        FROM film_oscars
        GROUP BY year
    )
    SELECT fo.year, fo.film_name, fo.total_oscars,fo.film_id
    FROM film_oscars fo
    JOIN max_oscars mo ON fo.year = mo.year
    WHERE fo.total_oscars = mo.max_oscars
    ORDER BY
        CASE
            WHEN fo.year LIKE '%/%' THEN CAST(SUBSTR(fo.year, 1, 4) AS INTEGER)
            ELSE CAST(fo.year AS INTEGER)
        END ASC,
        fo.total_oscars DESC;
    '''
    ceremony_data = mydb.execute(ceremony_query).fetchall()

    return render_template('most-awarded-search.html', ceremony_data=ceremony_data)