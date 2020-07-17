import gspread_dataframe as gd
import gspread
import pandas as pd
from sqlalchemy import create_engine
from oauth2client.service_account import ServiceAccountCredentials
import json
from pangres import upsert
import os
import sys
from string import punctuation


def create_keyfile_dict():
    """
    Creates a keyfile dictionary based on environment variables to be used in the oauth with google.\n
    Follow these directions to get the json credentials file <https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account>\n
    Copy and paste the credentials in your .env file with the following format:
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

    """
    variables_keys = {
        "type": os.environ.get("SHEET_TYPE"),
        "project_id": os.environ.get("SHEET_PROJECT_ID"),
        "private_key_id": os.environ.get("SHEET_PRIVATE_KEY_ID"),
        #this is so that python reads the newlines as newlines and not text
        "private_key": os.environ.get("SHEET_PRIVATE_KEY").replace('\\n',"\n"),
        "client_email": os.environ.get("SHEET_CLIENT_EMAIL"),
        "client_id": os.environ.get("SHEET_CLIENT_ID"),
        "auth_uri": os.environ.get("SHEET_AUTH_URI"),
        "token_uri": os.environ.get("SHEET_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.environ.get("SHEET_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.environ.get("SHEET_CLIENT_X509_CERT_URL")
    }
    if variables_keys['type'] == None:
        print('Issue with environment variables, please check that they have been set')
        sys.exit(1)
    return variables_keys

def get_df_from_gsheet(gsheet_name,worksheet_name='Sheet1'):
    """
    Gets data from a google sheet worksheet and puts it in a DataFrame.\n
    Authorises with google oauth based on the data specified in your environment variables (see `create_keyfile_dict()`).\n
    Make sure the Gsheet has been shared with your `client_email` from your json credential file from google.\n
    Opens the gsheet specified in gsheet_name and uses `Sheet1` if no worksheet_name is specified and puts the data in a dataframe.\n
    Selects all the non null columns and rows, and renames the columns to be db friendly.
    Parameters
    ----------
    gsheet_name : str
            Exact Name of Gsheet to extract data from. 
    worksheet_name : str, optional 
            Name of the worksheet to get the data from. (default is `Sheet1`)
    Returns
    -------
    A DataFrame containing the data in the google sheet.

    """
    try:
        k = create_keyfile_dict()
        #authorise with google
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(create_keyfile_dict(), scope)
        gc = gspread.authorize(credentials)
    except Exception as e: 
        print(e)
        print('Auth with google unsuccessful, please check your credentials')
        sys.exit(1)
    try:    
        #Open the gsheet and put the data into a df
        sheet = gc.open(gsheet_name).worksheet(worksheet_name)
        sheet_df = gd.get_as_dataframe(sheet,evaluate_formulas=True)
    except Exception as e:
        print(e)
        print('''Data extract from google sheet was unsuccessful.\nPlease check the name of the sheet and the worksheet, and that the client email specified in your env file has access to the sheet''')
        sys.exit(1)
    #find rows and columns with all nulls, to remove them from the df
    nans_rows = sheet_df[sheet_df.isnull().all(axis=1)].index[0]-1
    nans_columns = sheet_df.columns.drop(sheet_df.columns[sheet_df.isnull().all()])
    sheet_df = sheet_df.loc[:nans_rows,nans_columns]
    #change column names to be db friendly
    sheet_df.columns = [("".join([i for i in c if i not in punctuation.replace('_','')])).lower().strip().replace(' ','_') for c in sheet_df.columns]
    return sheet_df

def df_to_db(df, table_name,schema=None, index_name='index'):
    """
    Writes a DataFrame to a the specified table in the PostgreSQL database.\n
    If the table exisits, it will update the rows and insert new rows, otherwise it will create the table.\n
    This uses environment variables to access the DB. Make sure your .env file contains the following (replace with the relevant data):\n
    DB_USER= 'username'
    DB_PW = 'super_secret_password'
    DB_URL = 'db_address'
    DB_NAME = 'my_exciting_db_name'
    Parameters
    ----------
    df : DataFrame
        The DataFrame to write to the db. Make sure your columns of of the dtype you want in the db.
    table_name : str
        The `table_name` to update or create the table with in the DB.
    schema : str, optional
        The schema where the table should be located. (default in None, which refers to the `public` schema)
    index_name : str, optional
        The index name (must be the index of your df). Default is `index`.

    """
    #'postgresql://username:password@db_address/db'
    try:
        engine = create_engine('postgresql://'+os.environ.get('DB_USER') +':'+os.environ.get('DB_PW')+'@'+os.environ.get('DB_URL')+'/'+ os.environ.get('DB_NAME'))
    except Exception as e:
        print(e)
        print('Could not establish connection to db. Please check credentials in .env file')
        sys.exit(1)
    try:
        df.index.name = index_name
        upsert(engine=engine,
            df=df,
            table_name=table_name,
            if_row_exists='update',
            schema=schema,
            dtype=None)
    except Exception as e:
        print(e)
        print('Could not write data to the specified table, check that the db credentials in .env file are correct and have write permissions')
        sys.exit(1)