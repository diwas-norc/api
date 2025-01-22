import azure.functions as func
from openai import AzureOpenAI
import os

app = func.FunctionApp()

@app.route(route="test")
def main(req: func.HttpRequest) -> func.HttpResponse:

    api_version = "2024-12-01-preview"

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),  
        api_version=api_version,
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    assistant = client.beta.assistants.create(
        instructions="You are an AI assistant that can write code to help answer math questions",
        model="gpt-4o-mini",
        tools=[{"type": "code_interpreter"}]
    )

    print(assistant)
    return func.HttpResponse("Hello World!")
    # return completion.to_json()
        
    