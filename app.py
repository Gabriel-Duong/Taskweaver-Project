import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_core.runnables.config import RunnableConfig
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema.messages import HumanMessage, SystemMessage
from slide_agent import generate_slide_content, create_presentation, add_slide
from typing import cast

model = ChatOpenAI(streaming=True)
summarize_prompt = r"""
Hãy tóm tắt lại PDF này và làm nổi bật những điểm chính, bao gồm: 
- Ý chính.
- Những đóng góp.
- Thực nghiệm và kết quả.
- Kết luận
"""
# @cl.on_message
# async def main(message: cl.Message): #React to messages coming from the UI
#     """
#     Chainlit GUI entry point.
#     """
#     # Get user input
#     user_input = message.content

#     await cl.Message(content="🧠 Xây dựng nội dung...").send()

#     # Generate slide content
#     try:
#         slide_content = generate_slide_content(user_input)
#     except Exception as e:
#         await cl.Message(content=f"❌ OpenAI Error: {e}").send()
#         return

#     await cl.Message(content="📊 Thiết kế bản thuyết trình...").send()

#     # Create presentation
#     try:
#         presentation_title = "Generated AI Presentation"
#         presentation_id = create_presentation(presentation_title)
#     except Exception as e:
#         await cl.Message(content=f"❌ Google Slides Error: {e}").send()
#         return

#     await cl.Message(content="📑 Thiết kế slides...").send()

#     # Add slides
#     slides = slide_content.split("\n\n")
#     for i, slide in enumerate(slides):
#         if "\n" in slide:
#             title, body = slide.split("\n", 1)
#             add_slide(presentation_id, title.strip(), body.strip())

#     presentation_link = f"https://docs.google.com/presentation/d/{presentation_id}"
#     await cl.Message(content=f"✅ Hoàn tất! [View it here]({presentation_link})").send()

@cl.on_chat_start
async def on_chat_start(): #define a hook that is called when a new chat session is created
    await cl.Message(content=f"Xin chào, tôi là nhà thiết kế Google Slides từ PDF, vân vân").send()
    await cl.Message(content=f"Bạn có muốn thiết kế một bản thuyết trình từ file PDF không (Có hay không)").send()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Bạn là một nhà thiết kế đầy kinh nghiệm trong lĩnh vực tạo ra Google Slides từ PDF, vân vân."
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)
    
@cl.on_message
async def on_message(message: cl.Message):
    
    runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)
    await msg.send()

    #Read PDF
    if message.content.lower() == "có":
    # if ("pptx" in message.content.lower() or "thuyết trình" in message.content.lower()) and "pdf" in message.content.lower():
        loader = None
        pages = None
        messages = None
        summary_res = None
        description = None
        # Wait for the user to upload a file
        # while files == None:
        #     files = await cl.AskFileMessage(
        #         content="Please upload a file to begin!", accept=["application/pdf"]
        #     ).send()
        files = await cl.AskFileMessage(content="Hãy tải một file để bắt đầu!", accept = ["application/pdf"]).send()

        pdf_file = files
        loader = PyPDFLoader(pdf_file[0].path, extract_images=False)
        # Let the user know that the system is ready
        await cl.Message(
            content=f"`{pdf_file[0].name}` tải thành công"
        ).send()
    
    #Summarise the contents of the PDF
        pages = loader.load()
        messages = [
            SystemMessage(content=summarize_prompt),
            HumanMessage(content="Nội dung PDF là:" + "\n".join([c.page_content for c in pages])),
        ]
        summary_res = model.invoke(messages).content
        description = f"Tôi đã tóm tắt {len(pages)} trang của PDF." f"Tóm tắt về nội dung ta có: {summary_res}"

        #Chain of thought and creating slides
        await cl.Message(content=description).send()
        await cl.Message(content="🧠 Xây dựng nội dung...").send()
        # Generate slide content
        try:
            contents = summary_res 
            slide_content = generate_slide_content(contents)
        except Exception as e:
            await cl.Message(content=f"❌ OpenAI Error: {e}").send()
            return

        await cl.Message(content="📊 Thiết kế bản thuyết trình...").send()

        # Create presentation
        try:
            presentation_title = "Generated AI Presentation"
            presentation_id = create_presentation(presentation_title)
        except Exception as e:
            await cl.Message(content=f"❌ Google Slides Error: {e}").send()
            return

        await cl.Message(content="📑 Thiết kế slides...").send()

        # Add slides
        slides = slide_content.split("\n\n")
        for i, slide in enumerate(slides):
            if "\n" in slide:
                title, body = slide.split("\n", 1)
                add_slide(presentation_id, title.strip(), body.strip())

        presentation_link = f"https://docs.google.com/presentation/d/{presentation_id}"
        await cl.Message(content=f"✅ Hoàn tất! [View it here]({presentation_link})").send()    
       
    
    




    