from google import genai
from google.genai.types import HttpOptions

client = genai.Client(
    vertexai=True,
    project="code-fest",
    location="us-central1",
    http_options=HttpOptions(api_version="v1"),
)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='How does AI work?',
)
print(response.text)