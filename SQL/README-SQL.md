## Create a SQlite database for feedback_responses

### Main approach
  We create a SQLite database with four main tables: Categories, Courses, Feedback Instances and Feedback responses. We will parse json files that contain needed data for the database and we will store it inside the moodle_analytics.db database.

### How to run the parsing script and create SQLite database
  1. First we have to run the command below inside "SQL" folder to initialize our database:
     
  ```bash
  python3 ./create_db.py
  ```

  2. Place inside the "SQL" folder json files needed to be parsed. The program will automatically detect them.
  3. Run the main python script that will handle the parsing of our json files and will store information inside our database:

  ```bash
  python3 ./migrate.py
  ```

  4. A "moodle_analytics.db" file will be created and here we will have our final product. We can further visualise our newly made database inside the DB Browser app or any other prefered database visualizer app.

We have provided example images of how the database is populated at **SQL/screenshot_preview**.
