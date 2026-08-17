import os
from google import genai
import json


client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def ai_response(user_input, client,memory):
    prompt = f"""
You are an AI assistant.

The following is stored memory about the user:

{memory}

Use this memory only when it is relevant to the user's message.
Do not modify the memory.
Answer the user normally.

User message:
{user_input}
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )
  

    print("Ai", interaction.output_text)


def memory_storage(user_input, client):
    
    prompt = f"""
    You are a memory manager.

    Analyze this user message:

    {user_input}

    Decide what to do with the information.

    Possible actions:
    SAVE
    UPDATE
    DELETE
    NONE

    Return ONLY JSON in this format:

    {{
        "action": "SAVE",
        "key": "example",
        "value": "example",
        "needs_memory": true
    }}
    """

    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )
    global stored_value
    #stored_value = json.loads(response.output_text)
    stored_value = json.loads(response.output_text)

    with open("memory.json", "w") as file:
        json.dump(stored_value, file, indent=4)

def memory_retreve():
    with open("memory.json",'r') as file:
      stored_value = json.load(file)
    return stored_value
      
while True:
    user_input = input("Say something to AI: ")
    if user_input.lower() == "exit":
        print(""" 
        
This project demonstrates how AI can store, update, delete,
and recall user information across sessions.
        """)
        
        break
    try:
      memory = memory_retreve()
      ai_response(user_input,client,memory)
      
    except Exception as e:
      #print("x.......AI..........x")
      print(e)
    try:
      memory_storage(user_input, client)
    except Exception as e:
      #print("x........MeM.........x")
      print(e)
      print("AI didnt memories this")
      
      