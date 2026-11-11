from langchain_text_splitters import MarkdownHeaderTextSplitter
from config import saving_file
from gigachat import GigaChat
from config import create_key

def file_md(): 
    headers_to_split_on = [
        ("#", "header_1"),
        ("##", "header_2"),
        ("###", "header_3")
]   

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
)

    chunks = markdown_splitter.split_text(saving_file)

    for chunk in chunks: 
        ai_text = chunk.page_content

async def gigachat(message: str) -> str: 
    async with GigaChat(
        credentials=create_key, 
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    ) as giga: 

        response = await giga.achat({
            "model": "GigaChat-2",
            "message": [
                {"role": "system", "content": " твоя задача отвечать вежливо"}, 
                {"role": "user", "content": message }
            ],
            "temperature": 0.6
        })

        messages = response.choices[0].message.content




    