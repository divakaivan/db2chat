from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

import streamlit as st
import sqliteschema

import os

db_file = 'chinook.db'
db = SQLDatabase.from_uri(f'sqlite:///{db_file}')
# mixtral-8x7b-32768
# llama3-8b-8192
# llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)

def get_schema(_):
    schemas = ''
    for table in db.get_usable_table_names():
        schemas += db.get_table_info([table]).split('/*')[0].strip()
    return schemas

def get_sql_query_prompt_pipeline(llm):
    """Generate a data processing pipeline for prompting users to write SQL queries based on a given database schema."""

    template ="""
    You are a data analyst in a company who is interacting with a user that is asking you questions about the company's database.
    Based on the table schemas below, write a SQL query that would answer the user's question.
    
    <SCHEMA>{schema}</SCHEMA>

    Take the conversation history into account: {chat_history}

    Use the following couple of examples as reference for the ideal answer style:
    \nExample 1:
    Question: How many employees are there
    SQL Query: SELECT COUNT(*) FROM Employee;
    \nExample 2:
    Question: Find the total number of tracks in each genre
    SQL Query: SELECT g.Name AS Genre, COUNT(t.TrackId) AS NumberOfTracks FROM Track t JOIN Genre g ON t.GenreId = g.GenreId GROUP BY g.Name;

    Return only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks. 
    Do not use any special tokens either in your answer. 
    Do not use any special characters like \\.
    Make sure to return pure SQL.
    Now, it is your turn:
    
    Question: {question}
    SQL Query:
    """

    prompt = ChatPromptTemplate.from_template(template)

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query, db, chat_history, llm):
  sql_chain = get_sql_query_prompt_pipeline(llm)
  
  template = """
    You are a data analyst in a company who is interacting with a user that is asking you questions about the company's database.
    Based on the table schema below, conversation history, sql query and user question, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}

    Remove any \\ from the query, if such exist.
    SQL Query: {query}
    User question: {question}
    AI Response: {response}"""
  
  prompt = ChatPromptTemplate.from_template(template)
  query_result = sql_chain.invoke({'question': user_query, 'chat_history': chat_history})
  chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
      schema=lambda _: get_schema(_),
      response=lambda vars: db.run(vars['query']),
    )
    | prompt
    | llm
    | StrOutputParser()
  )

  result = chain.invoke({
    'question': user_query,
    'chat_history': chat_history,
  })
  print(f'{query_result=}')
  return result


if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
      AIMessage(content='Hello! Ask me anything about your database :)'),
    ]

st.set_page_config(page_title='Chat with your SQLite3 database')
st.title('Chat with your SQLite3 database')

if 'dbs' not in st.session_state:
    dbs = {}
    dbs['chinook'] = [SQLDatabase.from_uri(f'sqlite:///chinook.db'), 'chinook.db']
    dbs['northwind'] = [SQLDatabase.from_uri(f'sqlite:///northwind.db'), 'northwind.db']
    dbs['sakila'] = [SQLDatabase.from_uri(f'sqlite:///sakila.db'), 'sakila.db']
    st.session_state['dbs'] = dbs
else:
    dbs = st.session_state['dbs']

with st.sidebar:
    selectbox_llm = st.selectbox(
        'Which model would you like to use?',
        ('gpt-4-0125-preview', 'mixtral-8x7b-32768', 'gemma-7b-it', 'llama3-8b-8192'),
        index=1
    )
    api_key = st.text_input(label = 'Groq/OpenAI API key:', type='password')
    if selectbox_llm in ['mixtral-8x7b-32768', 'gemma-7b-it', 'llama3-8b-8192']:
        os.environ['GROQ_API_KEY'] = api_key
    else:
        os.environ['OPEN_AI_KEY'] = api_key
    uploaded_db = st.file_uploader(label='Upload your SQLite database file',type='sqlite')
    if uploaded_db:
        if st.button('Upload'):
            dbs[uploaded_db.name] = [SQLDatabase.from_uri(f'sqlite:///{uploaded_db.name}'), uploaded_db.name]
    selectbox_db = st.selectbox(
      'Which databast would you like to use?',
      st.session_state.dbs.keys(),
      index=None,
      placeholder='Select a database...',
    )
    selected_db = st.session_state.dbs['chinook']
    
    if selectbox_db:
        selected_db = st.session_state.dbs[selectbox_db]

    if st.button('Connect'):
        with st.spinner('Connecting to database...'):
            st.success(f"Connected to **{selected_db[1]}**")
    st.markdown(f'# {selected_db[1]}\'s schema')
    extractor = sqliteschema.SQLiteSchemaExtractor(selected_db[1])
    st.markdown(extractor.dumps(output_format='markdown', verbosity_level=1))

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message('AI'):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message('Human'):
            st.markdown(message.content)

user_query = st.chat_input('Type a message...')

if user_query is not None and user_query.strip() != '':
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message('Human'):
        st.markdown(user_query)
        
    with st.chat_message('AI'):
        try:
            llm = ChatGroq(model=selectbox_llm, temperature=0) if selectbox_llm in ['mixtral-8x7b-32768', 'gemma-7b-it', 'llama3-8b-8192'] else ChatOpenAI(model="gpt-4-0125-preview")
            response = get_response(user_query, selected_db[0], st.session_state.chat_history, llm)
            st.markdown(response)
            st.session_state.chat_history.append(AIMessage(content=response))
        except Exception as e:
            st.error(f'Oops! There was an error: {e}')
        
    

