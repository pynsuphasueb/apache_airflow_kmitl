import numpy as np
import pandas as pd
import sklearn
import psycopg2
import pickle
import re
import json
import csv
import requests
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import LinearSVC
from airflow import DAG
from datetime import datetime, timedelta
from airflow.sensors.http_sensor import HttpSensor
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.slack_operator import SlackAPIPostOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import LinearSVC




pd.set_option('max_rows', 500)
pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)

# pd.set_option('display.max_colwidth', None)
pd.set_option('max_colwidth', 400)
#pd.describe_option('max_colwidth')



def hook_data_to_csv():
    conn = psycopg2.connect(database="mydb", user='mydb', password='mydb', host='mydb')
    df = pd.read_sql('SELECT * FROM titanic_table', conn)
    print (df)
    df.to_csv('/opt/airflow/dags/files/titanic/data1.csv', index = False, header=True)
    return df

def hook_data_to_csv2():
    conn = psycopg2.connect(database="mydb", user='mydb', password='mydb', host='mydb')
    df = pd.read_sql('SELECT * FROM titanic_table', conn)
    print (df)
    df.to_csv('/opt/airflow/dags/files/titanic/data2.csv', index = False, header=True)
    return df

def load_data():
    # train_df = pd.read_csv(root + 'train.csv') 
    # test_df = pd.read_csv(root+ 'test.csv')
    # train_df = pd.read_csv('titanic/train.csv') 
    # train_df = pd.read_csv('/opt/airflow/dags/files/titanic/train.csv') 
    # # train_df = pd.read_csv('mnt/airflow/dags/files/titanic/train.csv')
    # test_df = pd.read_csv('/opt/airflow/dags/files/titanic/test.csv')
    # df = pd.concat([train_df, test_df])
    # return df, len(train_df)
    # df = pd.read_csv('/opt/airflow/dags/files/titanic/data2.csv')
    train_df = pd.read_csv('/opt/airflow/dags/files/titanic/data1.csv')
    df = pd.read_csv('/opt/airflow/dags/files/titanic/data2.csv')
    return df, len(train_df)
    

def clean_data(in_df):
    df = in_df.copy()
    df['CabinZone'] = 'Cabin-' + df['cabin'].str[0]
    cabinzonedf = pd.get_dummies(df['CabinZone'])
    df = pd.concat([df, cabinzonedf],axis=1)
    df['cabin'] = df['cabin'].fillna('nocabin')
    df.drop('CabinZone', axis=1, inplace = True)
    df['age'] = df['age'].fillna(df['age'].mean())
    df['embarked'] = df['embarked'].fillna(df['embarked'].mode()[0])
    return df

def getInitialFeature(df):
    initial = []
    for i in range(len(df)):
        name = df['name'].values[i]
        initial.append(name.split(',')[1].split('.')[0].strip())
    #x = np.array(initial) 
    #print(np.unique(x))
    df['initial'] = initial
    initial_cats  = [['Capt', 'Col', 'Don', 'Dr', 'Jonkheer', 'Lady', 'Major', 'Master', 'Miss', 'Mlle', 'Mme', 'Mr', 'Mrs', 'Ms', 'Rev', 'Sir', 'the Countess']]    
    initial_ohe = OneHotEncoder(categories = initial_cats)
    initial_feature_arr = initial_ohe.fit_transform(df[['initial']]).toarray()
    #confirm that categories are sorted in the same as pre-defined list
    #print(initial_ohe.categories_)
    initial_feature_labels = initial_cats[0]
    initialDummy = pd.DataFrame(initial_feature_arr, columns=initial_feature_labels)
    return initialDummy
    
def getAlphabetPrefixTicket(df):
    #alphaPrefixDict = []
    alphaPrefixTicket = []
    for i in range(len(df)):
        ticket = df['ticket'].values[i]
        res = re.findall('^[\w/.]+\s|$', ticket)[0]
        #res = re.findall('^[\w?.!/;:]+\s|$', ticket)[0]
    
        # res = re.search('^[\w/.]+\s|$', ticket).group()
        # alphaPrefixDict.append((ticket, res.strip()))
        
        ticketCode =  'Ticket-' + res.strip().translate({ord(i):None for i in '/.'})
        alphaPrefixTicket.append(ticketCode)
#     x = np.array(alphaPrefixTicket) 
#     print(np.unique(x))
    df['alphaPrefixTicket'] = alphaPrefixTicket
    alphaPrefix_cats  = [['Ticket-', 'Ticket-A4', 'Ticket-A5', 'Ticket-AS', 'Ticket-C', 'Ticket-CA',
         'Ticket-CASOTON', 'Ticket-FC', 'Ticket-FCC', 'Ticket-Fa', 'Ticket-PC',
         'Ticket-PP', 'Ticket-PPP', 'Ticket-SC', 'Ticket-SCA4', 'Ticket-SCAH',
         'Ticket-SCOW', 'Ticket-SCPARIS', 'Ticket-SCParis', 'Ticket-SOC', 'Ticket-SOP',
         'Ticket-SOPP', 'Ticket-SOTONO2', 'Ticket-SOTONOQ', 'Ticket-SP',
         'Ticket-STONO', 'Ticket-STONO2', 'Ticket-SWPP', 'Ticket-WC', 'Ticket-WEP']]
#     alphaPrefixDummy = pd.get_dummies(df['alphaPrefixTicket'], columns = alphaPrefix_cats, drop_first=True)
    
    alphaPrefix_ohe = OneHotEncoder(categories = alphaPrefix_cats, drop = 'first')
    alphaPrefix_feature_arr = alphaPrefix_ohe.fit_transform(df[['alphaPrefixTicket']]).toarray()
    #confirm that categories are sorted in the same as pre-defined list
    #print(alphaPrefix_ohe.categories_)
    alphaPrefix_cats[0].remove('Ticket-')
    alphaPrefix_feature_labels = alphaPrefix_cats[0]
    alphaPrefixDummy = pd.DataFrame(alphaPrefix_feature_arr, columns=alphaPrefix_feature_labels)
    return alphaPrefixDummy

def getOneHotEncodeSex(df):
    #x = np.array(df['Sex']) 
    #print(np.unique(x))
    sex_cats  = [['male', 'female']]
    sex_ohe = OneHotEncoder(categories = sex_cats, drop = 'first')
    sex_feature_arr = sex_ohe.fit_transform(df[['sex']]).toarray()
    #confirm that categories are sorted in the same as pre-defined list
    #print(sex_ohe.categories_)
    sex_cats[0].remove('male')
    sex_feature_labels = sex_cats[0]
    sexDummy = pd.DataFrame(sex_feature_arr, columns=sex_feature_labels)
    return  sexDummy 

def getOneHotEncodeEmbarked(df):
    #x = np.array(df['Embarked']) 
    #print(np.unique(x))
    embarked_cats  = [['C', 'Q', 'S']]
    embarked_ohe = OneHotEncoder(categories = embarked_cats, drop = 'first')
    embarked_feature_arr = embarked_ohe.fit_transform(df[['embarked']]).toarray()
    #confirm that categories are sorted in the same as pre-defined list
    #print(embarked_ohe.categories_)
    embarked_cats[0].remove('C')
    embarked_feature_labels = embarked_cats[0]
    embarkedDummy = pd.DataFrame(embarked_feature_arr, columns=embarked_feature_labels)
    return  embarkedDummy 

def extract_feat(in_df):
    feat = in_df.copy()
    initial = getInitialFeature(feat)
    sex = getOneHotEncodeSex(feat)
    alphaPrefix = getAlphabetPrefixTicket(feat)
    embarked = getOneHotEncodeEmbarked(feat)

    #print(initial.shape)
    #print(alphaPrefix.shape)
    feat.reset_index(drop=True, inplace=True)
    feat = pd.concat([feat, initial, sex, alphaPrefix, embarked],axis=1) 
    #feat = pd.concat([feat, initial],axis=1) 
    feat = feat.drop('passengerid', axis=1) # infinite features 
    feat = feat.drop('name', axis=1)            # infinite features 
    feat = feat.drop('sex', axis=1)               # have alterative features, one-hot female 
    feat = feat.drop('ticket', axis=1)            # have alterative features, AlphaPrefixTicket
    feat = feat.drop('cabin', axis=1)            # have alterative features, one-hot CabinZone 
    feat = feat.drop('embarked', axis=1)     # have alterative features, one-hot Embarked 
    feat = feat.drop('initial', axis=1)             # have alterative features, one-hot initial 
    feat = feat.drop('alphaPrefixTicket', axis=1) # have alterative features, one-hot alpha Prefix Ticket 
    #feat = feat._get_numeric_data() #magic method to filter in only numeric features
    return feat

def encode_data(df, DEBUG = False):
    gle = LabelEncoder()

    for col in df.columns:
        # print(col)
        if df[col].dtype == "object": #encode all columns that are categorical data
            if DEBUG:
                print("Encoding columns: " + col)
            labels = gle.fit_transform(df[col])
            mappings = {index: label for index, label in enumerate(gle.classes_)}
            #print(mappings)
            df[col] = labels
    return df

def sep_feature_target(df):
    label = df['survived']
    data = df.drop('survived', axis=1)
    return data, label


def train_model(feat, label):
    model = GradientBoostingClassifier(random_state=0)
#     model = LinearSVC(random_state=0, tol=1e-5)
    model.fit(feat, label)
    return model

def eval_acc(prediction, actual):
    acc = sum(prediction == actual) / len(actual)
    return acc

def run_pipeline():
    # 1. Get data
    df, no_train_example = load_data()

    # 2. Clean data
    df = clean_data(df)

    # 3. Extract feature and split data
    #----------------------------------------------
    # 3.1 extract features
    df = extract_feat(df)
    # 3.2 encode all categorical data
    df = encode_data(df, DEBUG=True)
    # 3.3 split data into train and test dataset based on input files loaded (Simple holdout spliting)
    train_df = df.iloc[0:no_train_example]
    test_df = df.iloc[no_train_example:]

    
    # 4. Train model
    #----------------------------------------------
    # 4.1 Split data into features and target 
    train_X, train_y = sep_feature_target(train_df)
    test_X, test_y = sep_feature_target(test_df)
    # 4.2 Train a model
    model = train_model(train_X, train_y)

    # 5. Prediction
    train_prediction = model.predict(train_X)
    test_prediction = model.predict(test_X)

    # 6. Evaluation
    train_acc = eval_acc(train_prediction, train_y)
    test_acc = eval_acc(test_prediction, test_y)
    
    bias = 1 - train_acc # train_err
    test_err = 1 - test_acc
    variance = test_err - bias

    return train_acc, test_acc, bias, variance

# train_acc, test_acc, bias, variance = run_pipeline()

# print("--------------------")
# print("Training Acc: " + str(train_acc))
# print("Test Acc: " + str(test_acc))
# print("Bias: " + str(bias))
# print("Varaince: " + str(variance))

def create_deployable_model():
    # 1. Get data
    df, no_train_example = load_data()
    # df = load_data()
    # 2. Clean data
    df = clean_data(df)

    # 3. Extract feature and split data
    #----------------------------------------------
    # 3.1 extract features
    df = extract_feat(df)
    # 3.2 encode all categorical data
    df = encode_data(df)
    
    # 4. Train model
    #----------------------------------------------
    # 4.1 Separate All Data (df) into Features (X) and Target (y)
    df_X, df_y = sep_feature_target(df)
    # 4.2 Train a to-deply model by all data using pre-defined hyper-parameter¶
    model = train_model(df_X, df_y)
    
    # 5. Save a trained model to a serialized object
    print("Save a trained model to...")
    # print(file)
    with open('/opt/airflow/dags/files/logtrained_model/trained_model.plk','wb') as f:
        pickle.dump(model, f)
    with open('/opt/airflow/dags/files/trained_model/trained_model.plk','wb') as f:
        pickle.dump(model, f)
    with open('/opt/airflow/dags/files/trained_model/trained_model-new.plk','wb') as f:
        pickle.dump(model, f)

# /usr/local/airflow/dags/files/trained_model/trained_model2.plk
default_args = {
    "owner" : 'airflow',
    "start_date" : datetime(2021, 9, 24),
    "depends_on_past" : False,
    "email_on_failure" : False,
    "email" : "fahpin306330@gmail.com",
    "retries" : 1,
    "retry_delay" : timedelta(minutes=5)
}


with DAG(dag_id = "titanic_data_pipeline",
schedule_interval = "@once",
tags=['titanic_real'] ,
default_args = default_args, 
catchup = False) as dag:

    create_titanic_table = PostgresOperator(
        task_id = "create_titanic_table",
        postgres_conn_id = "titanic_db",
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

    delete_titanic = PostgresOperator(
        task_id = "delete_titanic",
        postgres_conn_id = "titanic_db",
        sql ="""
            delete from titanic_table where 1=1
          """
    )

    csv_to_table = PostgresOperator(
        task_id="csv_to_table",
        postgres_conn_id = "titanic_db",
        sql="""
            copy titanic_table(PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked) from '/titanic/titanic.csv' WITH DELIMITER ',' CSV HEADER;
            """
        )
    
    hook_data = PythonOperator(
        task_id='hook_data',
        python_callable = hook_data_to_csv
        )

    new_csv_to_table = PostgresOperator(
        task_id="new_csv_to_table",
        postgres_conn_id = "titanic_db",
        sql="""
            copy titanic_table(PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked) from '/titanic/titanic-new.csv' WITH DELIMITER ',' CSV HEADER;
            """
        )

    hook_data2 = PythonOperator(
        task_id='hook_data2',
        python_callable = hook_data_to_csv2
        )

    run_trainmodel = PythonOperator(
        task_id = "run_trainmodel", 
        python_callable = run_pipeline
    )

    save_trained_model = PythonOperator(
        task_id = "save_trained_model", 
        python_callable = create_deployable_model
    )

    rename_log_trained_model = BashOperator(
        task_id = "rename_log_trained_model",
        bash_command = """cd /opt/airflow/dags/files/logtrained_model/ && \
            mv trained_model.plk trained_model-{{ds}}.plk"""
            #https://airflow.apache.org/docs/apache-airflow/stable/macros-ref.html?fbclid=IwAR0j2qiprHskhkdheh6GSkCjN9hJilX9LNhW0tNPotttnp90rEBFfmgaJXw#default-variables
    )

create_titanic_table >> delete_titanic >> csv_to_table >>  hook_data >> new_csv_to_table >> hook_data2 >> run_trainmodel >> save_trained_model >> rename_log_trained_model
