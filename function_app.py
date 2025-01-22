import azure.functions as func
from openai import AzureOpenAI
import os

app = func.FunctionApp()

@app.route(route="test")
def main(req: func.HttpRequest) -> func.HttpResponse:

    api_version = "2024-12-01-preview"

    deployment_client = AzureOpenAI(
        api_version=api_version,
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment="gpt-4o-mini",
    )

    completion = deployment_client.chat.completions.create(
        model="<ignored>",
        messages=[
            {
                "role": "user",
                "content": "How do I output all files in a directory using Python?",
            },
        ],
    )

    return completion.to_json()
        
    