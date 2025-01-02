from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
import os
load_dotenv()
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ['OPENAI_API_KEY'] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-05-01-preview"

llm=AzureChatOpenAI(deployment_name=os.getenv("azure_deployment"), temperature=0.5,api_version="2024-05-01-preview",
                          azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))


def generate_llm_response(response):

    llm_response = llm.invoke(response)
    # print(response.content)
    return llm_response.content

