from langchain_google_community import CalendarToolkit

toolkit = CalendarToolkit(credentials_path="credentials.json")

calendar_tools = toolkit.get_tools()
