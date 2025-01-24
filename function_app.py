import azure.functions as func
from openai import AzureOpenAI
import os
import io
import json

app = func.FunctionApp()

api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_KEY"],  
    api_version=api_version,
    azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
)

assistant = client.beta.assistants.retrieve("asst_RgysFE7vBPl7qZ0zteB3N2Ps")

# assistant = client.beta.assistants.create(
#     instructions="You are an AI assistant that can write code to help answer math questions",
#     model="gpt-4o-mini",
#     tools=[{"type": "code_interpreter"}]
# )

@app.route(route="test")
def main(req: func.HttpRequest) -> func.HttpResponse:
    # GPT-4o-mini
    # thread id thread_q0gqkDEvMcHxdQ8blYaiAtdp
    # assistant id: asst_jO539osPsw7xvpKcQUbRUS0a

    # GPT-35-turbo
    # thread_lj8jzsKJlzgJxBWtCRwWmBnm
    # thread id with llama txt file thread_W6gytKhwGeAMMSQ019iiL24o
    # asst_RgysFE7vBPl7qZ0zteB3N2Ps
    thread = client.beta.threads.retrieve("thread_W6gytKhwGeAMMSQ019iiL24o")
    # thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="What is the carbon footprint of training a Llama model?",
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please address the user as Jane Doe. The user has a premium account.",
    )

    print("Run completed with status: " + run.status)

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        messages_json = messages.to_json()
        # print(messages_json)
        return func.HttpResponse(messages_json)
    else:
        print("RUN FAILED: ", run)
        return func.HttpResponse("Run failed")
    

@app.route(route="chat")
def chat(req: func.HttpRequest) -> func.HttpResponse:
    thread_id = req.params.get('thread_id')
    message = req.params.get('message')

    files = req.get_json().get('files')
    
    print("Files: ", [file['name'] for file in files])
    client_files = []
    for file in files:
        content = file["content"]
        file_bytes = content.encode('utf-8')
        file_io = io.BytesIO(file_bytes)
        # file_io.name = file["name"]

        file_response = client.files.create(
            file=file_io,
            purpose="assistants"
        )
        client_files.append(file_response)

    # return func.HttpResponse(
    #     json.dumps({"data": [{"thread_id": thread_id, 
    #                           "message": message, 
    #                           "files": json.dumps([file.id for file in client_files])}
    #                         ]}))

    

    if not message:
        return func.HttpResponse("Please provide a message")
    
    # if thread_id is null or empty, create a new thread
    if not thread_id:
        thread = client.beta.threads.create()
    else:
        thread = client.beta.threads.retrieve(thread_id)

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="What is the carbon footprint of training a Llama model?",
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please address the user as Jane Doe. The user has a premium account.",
    )

    print("Run completed with status: " + run.status)

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        messages_json = messages.to_json()
        # print(messages_json)
        return func.HttpResponse(messages_json)
    else:
        print("RUN FAILED: ", run)
        return func.HttpResponse("Run failed")
    