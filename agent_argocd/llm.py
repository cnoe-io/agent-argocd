import os
from pydantic import SecretStr
from langchain_openai import AzureChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(model_type="azure-openai") -> str:
  model = None
  if model_type == "azure-openai":
    # Initialize the Azure OpenAI model
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY must be set as an environment variable.")

    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT must be set as an environment variable.")

    model = AzureChatOpenAI(
        api_key=SecretStr(api_key),
        azure_endpoint=azure_endpoint,
        model="gpt-4o",
        openai_api_type="azure_openai",
        api_version="2024-07-01-preview",
        temperature=0,
        max_retries=10,
        seed=42
    )
  # elif model_type == "google-gemini":
  #   if not os.getenv("GOOGLE_API_KEY"):
  #     raise ValueError("GOOGLE_API_KEY must be set as an environment variable.")

  #   model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')

  return model

