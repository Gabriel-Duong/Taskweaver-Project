import chainlit as cl
from slide_agent import generate_slide_content, create_presentation, add_slide

@cl.on_message
async def main(message: cl.Message):
    """
    Chainlit GUI entry point.
    """
    # Get user input
    user_input = message.content

    await cl.Message(content="🧠 Generating content...").send()

    # Generate slide content
    try:
        slide_content = generate_slide_content(user_input)
    except Exception as e:
        await cl.Message(content=f"❌ OpenAI Error: {e}").send()
        return

    await cl.Message(content="📊 Creating presentation...").send()

    # Create presentation
    try:
        presentation_title = "Generated AI Presentation"
        presentation_id = create_presentation(presentation_title)
    except Exception as e:
        await cl.Message(content=f"❌ Google Slides Error: {e}").send()
        return

    await cl.Message(content="📑 Adding slides...").send()

    # Add slides
    slides = slide_content.split("\n\n")
    for i, slide in enumerate(slides):
        if "\n" in slide:
            title, body = slide.split("\n", 1)
            add_slide(presentation_id, title.strip(), body.strip())

    presentation_link = f"https://docs.google.com/presentation/d/{presentation_id}"
    await cl.Message(content=f"✅ Presentation complete! [View it here]({presentation_link})").send()
