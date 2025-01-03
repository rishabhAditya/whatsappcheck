from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ['OPENAI_API_KEY'] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-05-01-preview"

llm = AzureChatOpenAI(deployment_name=os.getenv("azure_deployment"), temperature=0.5, api_version="2024-05-01-preview",
                      azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))

prompt = ChatPromptTemplate.from_template(
    "You are a highly knowledgeable and empathetic medical assistant."
    "Your primary role is to provide accurate, reliable, and up-to-date medical information to users."
    "You can answer questions about symptoms, treatments, medications, medical conditions, and general health advice."
    "Questions which are  not medical queries should be responded with only 'Only medical queries allowed'."
    "\n"
    "QUESTION: {question}"
)


def generate_llm_response(question: str) -> str:
    # llm_response = llm.invoke(question)
    chain = prompt | llm | StrOutputParser()
    # print(response.content)
    llm_response = chain.invoke({"question": question})
    # print(llm_response)
    #
    return llm_response
