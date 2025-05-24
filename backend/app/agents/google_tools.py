from langchain_google_community import CalendarToolkit
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)


credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/", "https://www.googleapis.com/auth/calendar"],
    client_secrets_file="credentials.json",
)

api_resource = build_resource_service(credentials=credentials)

gmail_toolkit = GmailToolkit(api_resource=api_resource)

gmail_tools = gmail_toolkit.get_tools()


calendar_toolkit = CalendarToolkit(credentials_path="credentials.json")

calendar_tools = calendar_toolkit.get_tools()
