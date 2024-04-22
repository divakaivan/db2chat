# This is db2chat - chat with your (SQLite) database
Hosted webapp: [https://db2chat.streamlit.app/](https://db2chat.streamlit.app/)

You will need a *free* [Groq](https://console.groq.com/keys) or a paid [OpenAI](https://openai.com/blog/openai-api) API key to execute queries.

There are 3 default databases loaded in the webapp:

- [chinook](https://github.com/lerocha/chinook-database)
- [northwind](https://github.com/jpwhite3/northwind-SQLite3/tree/main)
- [sakila](https://www.kaggle.com/datasets/atanaskanev/sqlite-sakila-sample-database)

## How to use

1. Input your Groq/OpenAI API key and select a model (mistral-8x7b, gpt-4, llama3-8b, gemma-7b-it)
<img width="306" alt="image" src="https://github.com/divakaivan/db2chat/assets/54508530/3c3329b2-fa70-4116-8868-cb810695e28e">

2. Load your sqlite3 db file (optional)
<img width="292" alt="image" src="https://github.com/divakaivan/db2chat/assets/54508530/c5cfb669-8a78-4bae-bff8-5f3ad629c929">

3. Select a database to chat with (default is chinook) + click 'Connect'
<img width="304" alt="image" src="https://github.com/divakaivan/db2chat/assets/54508530/0d1659c5-bf04-40c2-a648-74bb0d1d6bbc">

You can view your db's schema:

<img width="519" alt="image" src="https://github.com/divakaivan/db2chat/assets/54508530/49a8d53e-916d-4224-bffa-a9bc4e61468d">

4. Enter a query, run and get your chart
<img width="731" alt="image" src="https://github.com/divakaivan/db2chat/assets/54508530/e054998b-1afa-4fba-8123-cd8b1544e046">

You can see the executed SQL query by hovering the (?)

<img width="601" alt="image" src="https://github.com/divakaivan/db2chat/assets/54508530/2b827177-3d65-4228-af17-aa37d958bfee">
   
## Why SQLite?
I wanted the app to be less dependant on outside/hosted services. With sqlite3's file databases (size is small as well), the concept of talking with a database can be easily demonstrated

#### Known limitations
- The model might generate special characters when calling variables/tables. For troubleshooting, the returned error includes the problematic SQL query
- Using general-purpose off-the-shelf models
