import openai
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# 🔑 OpenAI API Key (Hardcoded for now, or use os.getenv for env variables)
openai.api_key = "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"  # Replace with your actual API key

# 🔑 Google Slides API Authentication
SCOPES = ['https://www.googleapis.com/auth/presentations']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
slides_service = build('slides', 'v1', credentials=creds)


# 📝 Generate Slide Content Using OpenAI
def generate_slide_content(prompt):
    """
    Generate slide content using OpenAI Chat API.
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Use 'gpt-4' if you have access
        messages=[
            {"role": "system", "content": "You are an AI assistant that generates presentation slide content."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()


# 🖥️ Create a New Google Slides Presentation
def create_presentation(title):
    """
    Create a new Google Slides presentation and return its ID.
    """
    presentation = slides_service.presentations().create(body={
        'title': title
    }).execute()
    print(f"✅ Presentation created with ID: {presentation['presentationId']}")
    return presentation['presentationId']


# 📊 Add a Slide with Title and Content
def add_slide(presentation_id, title, content):
    """
    Add a slide with dynamically retrieved object IDs for title and content.
    """
    # Step 1: Create a new slide
    slide_creation_response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={
            "requests": [
                {
                    "createSlide": {
                        "slideLayoutReference": {
                            "predefinedLayout": "TITLE_AND_BODY"
                        }
                    }
                }
            ]
        }
    ).execute()

    # Step 2: Retrieve Object IDs
    slide_id = slide_creation_response['replies'][0]['createSlide']['objectId']
    print(f"✅ Slide created with ID: {slide_id}")

    # Fetch object IDs for title and body placeholders
    slide = slides_service.presentations().get(presentationId=presentation_id).execute()
    page_elements = next(
        (p['pageElements'] for p in slide['slides'] if p['objectId'] == slide_id),
        []
    )

    title_id = None
    body_id = None

    for element in page_elements:
        if 'shape' in element:
            shape_type = element['shape']['shapeType']
            if shape_type == 'TITLE':
                title_id = element['objectId']
            elif shape_type == 'BODY':
                body_id = element['objectId']

    if not title_id or not body_id:
        raise ValueError("❌ Could not find title or body object IDs on the slide.")

    # Step 3: Add Title and Body Text
    requests = [
        {
            "insertText": {
                "objectId": title_id,
                "text": title
            }
        },
        {
            "insertText": {
                "objectId": body_id,
                "text": content
            }
        }
    ]

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    print(f"✅ Slide added successfully: Title - '{title}'")

