import datetime
import psycopg2
import pandas as pd
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python_operator import PythonOperator
# create_pet_table, populate_pet_table, get_all_pets, and get_birth_date are examples of tasks created by
# instantiating the Postgres Operator


def get_activated_sources():
    request = "SELECT * FROM titanic_nine"
    pg_hook = PostgresHook(host = "mydb", prosgre_conn_id="titanic_db", schema = "mydb", login = "mydb", password = "mydb")
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(request)
    sources = cursor.fetchall()
    for source in sources:
        print(source)
    return sources


def tester():
    # Connect to your postgres DB
    # conn = psycopg2.connect(database="mydb", user='mydb', password='mydb', host='mydb')
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM titanic_t3;")
    # a = cur.fetchall()
    # a = str(a)
    # df = pd.DataFrame([[ij for ij in i] for i in a])
    # df.rename(columns={0: "PassengerId", 1: "Survived", 2: "Pclass", 3: "Name", 4: "Sex", 5: "Age", 6: "SibSp", 7:"Parch", 8:"Ticket", 9:"Fare", 10:"Cabin", 11:"Embarked"}, inplace=True)
    # return df


    # # Open a cursor to perform database operations
    # cur = conn.cursor()

    # # Execute a query
    # cur.execute("SELECT * FROM titanic_tenn")

    # # Retrieve query results
    # records = cur.fetchall()
    # return records

    conn = psycopg2.connect(database="mydb", user='mydb', password='mydb', host='mydb')
    df = pd.read_sql('SELECT * FROM titanic_t10', conn)
    print (df)
    df.to_csv(r'./dags/files/titanic/train_success.csv', index = False, header=True)
    return df

def tester2():
    conn = psycopg2.connect(database="mydb", user='mydb', password='mydb', host='mydb')
    df = pd.read_sql('SELECT * FROM titanic_t10', conn)
    print (df)
    df.to_csv(r'./dags/files/titanic/all_success.csv', index = False, header=True)
    return df

    

with DAG(
    dag_id="postgres_operator_dag",
    start_date=datetime.datetime(2020, 2, 2),
    schedule_interval="@once",
    tags= ["titanic_db"], 
    catchup=False,
    ) as dag:

    create_titanic_table = PostgresOperator(
        task_id = "create_titanic_table",
        postgres_conn_id = "titanic_db",
        sql ="""
            CREATE TABLE IF NOT EXISTS titanic_t10(
            PassengerId SERIAL PRIMARY KEY,
            Survived VARCHAR NULL,
            Pclass INT NULL,
            Name VARCHAR NULL,
            Sex VARCHAR NULL,
            Age FLOAT NULL,
            SibSp INT NULL,
            Parch INT NULL,
            Ticket VARCHAR NULL,
            Fare FLOAT NULL,
            Cabin VARCHAR NULL,
            Embarked VARCHAR NULL);

          """
    )

    csv_to_table = PostgresOperator(
        task_id="csv_to_table",
        postgres_conn_id = "titanic_db",
        sql="""
            copy titanic_t10(PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked) from '/var/lib/postgresql/data/files/titanic/train.csv' WITH DELIMITER ',' CSV HEADER;
            """
        )


    get_all = PostgresOperator(
        task_id="get_all",
        postgres_conn_id = "titanic_db",
        sql="SELECT * FROM titanic_t10 ;")

    # get_birth_date = PostgresOperator(
    #     task_id="get_birth_date",
    #     sql="""
    #         SELECT * FROM pet
    #         WHERE birth_date
    #         BETWEEN SYMMETRIC DATE '{{ params.begin_date }}' AND DATE '{{ params.end_date }}';
    #         """,
    #     params={'begin_date': '2020-01-01', 'end_date': '2020-12-31'},
    # )

    hook_task = PythonOperator(
        task_id='hook_task',
        python_callable = tester
        )
    
    new_csv_to_table = PostgresOperator(
        task_id="new_csv_to_table",
        postgres_conn_id = "titanic_db",
        sql="""
            copy titanic_t10(PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked) from '/var/lib/postgresql/data/files/titanic/test.csv' WITH DELIMITER ',' CSV HEADER;
            """
        )

    hook_all_task = PythonOperator(
        task_id='hook_all_task',
        python_callable = tester2
        )

    create_titanic_table >> csv_to_table >> get_all >> hook_task >> new_csv_to_table >> hook_all_task
    