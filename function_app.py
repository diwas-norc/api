import azure.functions as func
from openai import AzureOpenAI
import os

app = func.FunctionApp()

api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_KEY"],  
    api_version=api_version,
    azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
)

assistant = client.beta.assistants.retrieve("asst_jO539osPsw7xvpKcQUbRUS0a")

# assistant = client.beta.assistants.create(
#     instructions="You are an AI assistant that can write code to help answer math questions",
#     model="gpt-4o-mini",
#     tools=[{"type": "code_interpreter"}]
# )

@app.route(route="test")
def main(req: func.HttpRequest) -> func.HttpResponse:

    # thread id thread_q0gqkDEvMcHxdQ8blYaiAtdp
    # assistant id: asst_jO539osPsw7xvpKcQUbRUS0a
    thread = client.beta.threads.retrieve("thread_q0gqkDEvMcHxdQ8blYaiAtdp")
    # thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
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
        print(messages_json)
        return func.HttpResponse(messages_json)
    else:
        print("RUN FAILED: ", run)
        return func.HttpResponse("Run failed")
        
    