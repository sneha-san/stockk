from newsdataapi import NewsDataApiClient
from dotenv import load_dotenv
import os
load_dotenv(".env")

api_key = os.getenv("NEWS_DATA")

api = NewsDataApiClient(apikey=api_key)

def get_news(query ,category,language, country):
    response = api.news_api(category=category,language=language,q=query,qInTitle=None, country = country)
    return response


