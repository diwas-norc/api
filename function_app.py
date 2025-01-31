import base64
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

assistant = client.beta.assistants.retrieve("asst_3eetENdbDuCxDLfSA3F35QNe")

# assistant = client.beta.assistants.create(
#     instructions="You are an AI assistant that can write code to help answer math questions",
#     model="gpt-4o-mini",
#     tools=[{"type": "code_interpreter"}]
# )

@app.route(route="test_endpoint", methods=["GET", "POST"], auth_level="anonymous")
def test_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello, World!")

@app.route(route="test", methods=["GET", "POST"], auth_level="anonymous")
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
    

@app.route(route="chat", methods=["POST"], auth_level="anonymous")
def chat(req: func.HttpRequest) -> func.HttpResponse:
    req_body = req.get_json()
    thread_id = req_body.get('thread_id')
    message = req_body.get('message')

    files = req_body.get('files')
    
    client_files = []
    if files is not None:
        print("Files: ", [file['name'] for file in files])
        for file in files:
            content = file["content"]
            decoded_data = base64.b64decode(content)
            file_io = io.BytesIO(decoded_data)
            file_io.name = file["name"]

            file_response = client.files.create(
                file=file_io,
                purpose="assistants"
            )
            client_files.append(file_response)
    
    if not message:
        return func.HttpResponse("Please provide a message", status_code=400)
    
    if not thread_id:
        thread = client.beta.threads.create()
    else:
        thread = client.beta.threads.retrieve(thread_id)

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message,
        attachments=[{"file_id": c.id, "tools": [{"type":"file_search"}]} for c in client_files]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        extra_query={
            "include":["step_details.tool_calls[*].file_search.results[*].content"],
        }
        # instructions="Please format your response in markdown.",
    )

    print("Run completed with status: " + run.status)

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        message_json = get_citations(messages.data[0]).to_json()
        # message_json = messages.to_json()
        return func.HttpResponse(message_json)
        # return func.HttpResponse(messages.data[0].to_json())
    else:
        print("RUN FAILED: ", run)
        return func.HttpResponse("Run failed")

def get_citations(message):
    
    message_content = message.content[0].text
    annotations = message_content.annotations
    citations = []
    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' 【{index}】')
        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f'【{index}】{cited_file.filename}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            cited_file = client.files.retrieve(file_path.file_id)
            citations.append(f'【{index}】 {cited_file.filename}')
            # Note: File download functionality not implemented above for brevity
    
    if len(citations) > 0:
        message_content.value += '\n\n' + '\n'.join(sorted(set(citations)))

    return message