# g2pg
g2pg takes a Google Sheet, converts it to a DataFrame, which you can then manipulate as you need to.
This DataFrame can then be written to a PostgreSQL database table.
This makes use of a `.env` file, which after much trial and error I finally got to work with gspread.

### How does it work
g2pg uses the `gspread` package to extract data from the Google Sheet. 
Follow these directions to get the json credentials file that can  be used with `gspread` <https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account>
The json credentials need to be stored in a `.env` file. Don't upload the contents of your .env or json_credentials file to github unless you want everyone to know your secrets.

If using this package you need to have a `.env` file or enviroment variables set in the following way.

    DB_USER= 'username'
    DB_PW = 'super_secret_password'
    DB_URL = 'db_address'
    DB_NAME = 'db_name'

    SHEET_TYPE= 'service_account'
    SHEET_PROJECT_ID= 'api-project-XXX'
    SHEET_PRIVATE_KEY_ID= '2cd … ba4'
    SHEET_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n"
    SHEET_CLIENT_EMAIL= 'yoursisdifferent@developer.gserviceaccount.com'
    SHEET_CLIENT_ID= '1234567890'
    SHEET_AUTH_URI= 'https://accounts.google.com/o/oauth2/auth'
    SHEET_TOKEN_URI= 'https://oauth2.googleapis.com/token'
    SHEET_AUTH_PROVIDER_X509_CERT_URL= 'https://www.googleapis.com/oauth2/v1/certs'
    SHEET_CLIENT_X509_CERT_URL= 'https://www.googleapis.com/robot/v1/metadata/bla...bla..bla.iam.gserviceaccount.com'

There are 2 methods available:
* `def get_df_from_gsheet(gsheet_name,worksheet_name)`
    This returns a datframe from the specified Google Sheet and worksheet.The worksheet name is optional and will default to `Sheet1`.
    The dataframe will have all columns and rows removed, where there is no data, and the column names will be converted to a database friendly format.
* `def df_to_db(df, table_name,schema, index_name)`
    This writes the specified `df` to the `table_name` in the DB that is specified in the `.env` file.
    `schema` is optional and will default to `public` in postgres if not specified.
    `index_name` is the index of your df. If not specified, it will default to index (this is used as the primary key in your DB table).

