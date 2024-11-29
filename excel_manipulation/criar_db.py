import sqlite3

# Connect to SQLite database (creates 'oscars.db' if it doesn't exist)
connection = sqlite3.connect("oscars.db")
cursor = connection.cursor()

# Create Films table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Films (
    film_id INTEGER(3) PRIMARY KEY,
    year INTEGER(4),
    name VARCHAR(100)
);
""")

# Create Cerimonies table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Cerimonies (
    cerimony_id INTEGER(4) PRIMARY KEY,
    year INTEGER(4)
);
""")

# Create Classes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Classes (
    class_id INTEGER(2) PRIMARY KEY,
    year INTEGER(4),
    name VARCHAR(100),
    FOREIGN KEY (year) REFERENCES Cerimonies(year)
);
""")

# Create Categories table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Categories (
    category_id INTEGER(2) PRIMARY KEY,
    class_id INTEGER(2),
    name VARCHAR(100),
    original_name VARCHAR(100),
    FOREIGN KEY (class_id) REFERENCES Classes(class_id)
);
""")

# Create Nominees table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Nominees (
    nominees_id INTEGER(4) PRIMARY KEY,
    category INTEGER(2),
    film INTEGER(3),
    detail VARCHAR(100000),
    vote INTEGER(10),
    citation VARCHAR(100000),
    winner BOOLEAN,
    FOREIGN KEY (category) REFERENCES Categories(category_id),
    FOREIGN KEY (film) REFERENCES Films(film_id)
);
""")

# Create Entities table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Entities (
    entity_id INTEGER(5) PRIMARY KEY,
    name VARCHAR(100),
    job VARCHAR(100),
    multifilm_nomination BOOLEAN
);
""")

# Create Nominations table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Nominations (
    nominees_id INTEGER(4),
    entity_id INTEGER(5),
    PRIMARY KEY (nominees_id, entity_id),
    FOREIGN KEY (nominees_id) REFERENCES Nominees(nominees_id),
    FOREIGN KEY (entity_id) REFERENCES Entities(entity_id)
);
""")

# Commit and close the connection
connection.commit()
connection.close()

print("Database 'oscars.db' created successfully with all tables.")
