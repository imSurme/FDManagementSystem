# Requirements

| Command                              | Description                              |
|--------------------------------------|------------------------------------------|
| `pip install Flask`                  | Installs the Flask framework.            |
| `pip install mysql-connector-python` | Provides MySQL database connectivity.    |
| `pip install flask-session`          | Enables server-side session management.  |

### Configure MySQL Connection

To connect your application to the local MySQL database, update the following part of the code in your project:

```python
connection = mysql.connector.connect(
    host="FILL_HERE",
    user="FILL_HERE",
    passwd="FILL_HERE",
    database="FILL_HERE"
)
