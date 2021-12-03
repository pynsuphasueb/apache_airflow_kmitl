import datetime
import psycopg2
import pandas as pd
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python_operator import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
# create_pet_table, populate_pet_table, get_all_pets, and get_birth_date are examples of tasks created by
# instantiating the Postgres Operator


with DAG(
    dag_id="phptest",
    start_date=datetime.datetime(2020, 2, 2),
    schedule_interval="@once",
    tags= ["phptest"], 
    catchup=False,
    ) as dag:

    create_table = MySqlOperator(
        task_id='create_table',
        mysql_conn_id = 'phpmyadmin',
        sql ="""
            CREATE TABLE IF NOT EXISTS titanic_table(
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
    

create_table
    