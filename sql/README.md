# Use an SQLite Database to Store Feedback Data

## Main Approach
We create a SQLite database with four main tables: `Categories`, `Courses`, `Feedback Instances` and `Feedback responses`.
We will parse json files that contain needed data for the database and we will store it inside the moodle_analytics.db database.

## Run
1. First we have to run the command below inside `SQL/` directory to initialize our database:
     
```console
python3 ./create_db.py
```

2. Place inside the `SQL/` directory JSON files needed to be parsed.
   The program will automatically detect them.
3. Run the main Python script that will handle the parsing of our JSON files and will store information inside our database:

```console
python3 ./migrate.py
```

4. A `moodle_analytics.db` file will be created and here we will have our final product.
   We can further visualise our newly made database inside the DB Browser app or any other prefered database visualizer app.

We have provided example images of how the database is populated at **SQL/screenshot_preview**.
