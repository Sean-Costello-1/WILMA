#Import the necessary libraries
import openai   #Source: https://platform.openai.com/docs/api-reference?lang=python
from pymongo.mongo_client import MongoClient    #Source: https://pymongo.readthedocs.io/en/stable/tutorial.html
from pymongo.server_api import ServerApi
import re   #Source: https://docs.python.org/3/library/re.html

#Set OpenAI API key
openai.api_key = "INSERT_API_KEY_HERE"

#Replace the placeholder with the Atlas connection string
uri = "mongodb+srv://scostello:INSERT_PASSWORD.xmcpohb.mongodb.net/?retryWrites=true&w=majority&appName=WILMA"

#Set the Stable API version when creating a new client
client = MongoClient(uri, server_api=ServerApi('1'))

#Set the database name
db = client["PlayerData"]

#Set the collection name
collection = db["LoL"]

#Test the connection to the MongoDB deployment
#Source: https://www.mongodb.com/docs/drivers/pymongo/
def test_MongoDB_connection():
    #Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(e)

#Configure the chatbot
messages = [{"role": "system", "content": "You are a video game profile matching assistant named WILMA."}]

def get_players(rank, roles):
    query = {
        #100 points is the difference of 1 rank in League of Legends
        "rank": {"$gt": rank - 100, "$lt": rank + 100}, #Source: https://www.mongodb.com/docs/manual/reference/operator/query/gt/
        "roles": {"$in": roles}
    }
    return list(collection.find(query))

def parse_response(text):
    #Regular expressions
    rank = int(re.search(r'rank (\d+)', text).group(1))
    roles = re.findall(r'plays? ([a-z]+)', text)
    return rank, roles

def match_players(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model = "gpt-4-turbo",
        messages = [{"role": "system", "content": "You are a matchmaking assistant."},
                  {"role": "user", "content": user_input}]
    )
    return response.choices[0].message['content']

def main():
    while True:
        #Get user input or exit
        user_input = input("How may I assist you (type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        # Process user input with GPT-4 Turbo
        response = match_players(user_input)
        print("Assistant:", response)

        # Extract game parameters from the GPT-4 Turbo response
        try:
            rank, roles = parse_response(response)
            players = get_players(rank, roles)
            if players:
                print("Here are some potential matches for you:", players)
            else:
                print("No matches found. Please try again later.")
        except Exception as e:
            print("An error occurred while parsing the GPT-4 response or fetching the player data:", str(e)

if __name__ == "__main__":
    main()