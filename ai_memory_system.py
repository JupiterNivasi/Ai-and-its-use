import os
from google import genai
import json

# Connect to Gemini
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


def designAi(user_input, client):
    try:
        with open("memory.json", "r") as file:
            memory = json.load(file)
    except FileNotFoundError:
        memory = {}

    chat = client.chats.create(
        model="gemini-3-flash-preview",
        config={
            "system_instruction": """
You are a memory decision AI.

Your job is to analyze the user's message and determine whether
the user's memory needs to be changed.

AVAILABLE ACTIONS:

SAVE = The user has provided NEW information about themselves
that should be remembered.

UPDATE = The user has changed information that is already
stored in memory.

DELETE = The user wants previously stored information to be
forgotten or removed.

PASS = Nothing in memory needs to be changed.
This includes:
- normal conversation
- questions that can be answered using existing memory
- when you have already checked memory and there is nothing new
to save, update, or delete

EXIT = The user wants to end the program.

IMPORTANT:
Existing memory will be provided to you.

Before deciding the action, compare the user's message with
the existing memory.

If the information is ALREADY stored and the user is simply
talking about it or asking about it, choose PASS.

Do NOT save duplicate information.

If the user provides information that conflicts with existing
memory, choose UPDATE instead of SAVE.

Return a normal conversational response first.

At the very end, return exactly one JSON object:

{"action":"pass"}

The action MUST be exactly one of:
save, update, delete, pass, exit

Never choose more than one action.
"""
        }
    )

    prompt = f"""
EXISTING MEMORY
{json.dumps(memory, indent=2)}

USER MESSAGE
{user_input}
"""

    response = chat.send_message(prompt)

    return response.text


def flow_ai_des(response):
    save = False
    update = False
    delete = False
    pass_ = False
    exit_ = False

    json_text = response[response.rfind("{"):]

    data = json.loads(json_text)

    action = data["action"]

    if action == "save":
        save = True

    elif action == "update":
        update = True

    elif action == "delete":
        delete = True

    elif action == "pass":
        pass_ = True

    elif action == "exit":
        exit_ = True

    return save, update, delete, pass_, exit_


def JSON_AI(user_input, client, action):
    try:
      with open("memory.json", "r") as file:
        memory = json.load(file)
    except FileNotFoundError:
      memory = {}

    prompt = f"""
You are the memory manager.

User message:
{user_input}

Required action:
{action}

Your job is to process the required action.

Actions:

SAVE:
Save new information from the user.
Choose a clear key and store the relevant value.

UPDATE:
Update information that already exists.
Use the same key when possible.

DELETE:
Identify the key of the information that should be removed.

NONE:
Do nothing.

Return ONLY valid JSON.
Do not include explanations, markdown, or extra text.

Return exactly this format:

{{
    "action": "{action}",
    "key": "example",
    "value": "example"
}}
"""

    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    stored_value = json.loads(response.output_text)

    data = json.loads(response.output_text)

    key = data["key"]
    value = data["value"]

    try:
        with open("memory.json", "r") as file:
            memory = json.load(file)
    except FileNotFoundError:
        memory = {}

    if action == "DELETE":
      return key

    memory[key] = value

    with open("memory.json", "w") as file:
      json.dump(memory, file, indent=4)


while True:
    user_input = input("Say something: ")

    response = designAi(user_input, client)

    save, update, delete, pass_, exit_ = flow_ai_des(response)

    normal_response = response[:response.rfind("{")].strip()

    print(normal_response)

    if exit_:
        break

    elif pass_:
        print("pass is being executed")

    elif save:
        JSON_AI(user_input, client, "SAVE")
        print("save is being executed")

    elif update:
        JSON_AI(user_input, client, "UPDATE")
        print("update is being executed")

    elif delete:

        key = JSON_AI(user_input, client, "DELETE")

        with open("memory.json", "r") as file:
            memory = json.load(file)

        if key in memory:
            del memory[key]

        with open("memory.json", "w") as file:
            json.dump(memory, file, indent=4)

        print("delete is being executed")

    else:
        print("nothing executed")