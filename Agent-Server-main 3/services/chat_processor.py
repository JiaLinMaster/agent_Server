import asyncio
import datetime
import logging

from langchain_community.vectorstores import Chroma

from .prompts import get_rag_prompt, get_no_need_prompt
from config import settings

def build_chat_history(role, content):
    """构建单条对话记录"""
    return {
        "role": role,
        "timestamp": datetime.datetime.now().isoformat(),
        "content": content
    }

async def judge_if_need_rag(chat_history, client):
    """判断是否需要RAG检索"""
    # 构建判断需求的prompt
    judge_prompt = f"""
    角色：
    你是一个需求识别助手。分析以下电商bot与user的对话记录，判断用户最新的对话是否有明确需求。
    如果有(比如需要查询商品信息)，请将用户的需求重构为一句话（要是一段有主语实体，有明确需求的话，有可能会包含多个需求），明确当前需求，这句话我将用于向量检索；
    如果没有(比如用户的需求已被解决回复‘好的、谢谢’等)，请直接返回"无需求"。
    
    对话内容:
    {chat_history}

    输出要求：
    仅返回需求重构后的一句话，或者 无需求，禁止返回其余内容
    """
    
    # 调用DeepSeek API
    completion = await asyncio.to_thread(client.chat.completions.create,
                                         model=settings.MODEL_NAME,
                                         messages=[
                                             {"role": "system", "content": "你是需求识别助手"},
                                             {"role": "user", "content": judge_prompt}
                                         ],
                                         temperature=settings.MODEL_TEMPERATURE)
    result = completion.choices[0].message.content.strip()
    return result

async def process_multi_turn_chat(chat_history: list, vectorstore: Chroma, client):
    """
    处理多轮对话，根据是否需要RAG调用不同的流程
    :param chat_history: 对话历史记录
    :param vectorstore: 向量数据库对象
    :param client: LLM客户端对象
    :return: 客服回复内容
    """
    # 判断是否需要RAG
    need_rag = await judge_if_need_rag(chat_history, client)

    # 无需求，使用无RAG的prompt
    if need_rag == "无需求":
        logging.debug(f"{chat_history[-1]}无需RAG")
        prompt = get_no_need_prompt(chat_history)
    # 有需求，使用RAG流程
    else:
        logging.debug(f"{chat_history[-1]}需要RAG")
        # 提取相似文档
        similar_docs = vectorstore.similarity_search_with_score(
            query=need_rag,
            k=3
        )
        product_info = '\n'.join([doc[0].page_content for doc in similar_docs])
        # 获取RAG提示词
        prompt = get_rag_prompt(chat_history, product_info)

    # 调用DeepSeek API生成回复
    completion = await asyncio.to_thread(client.chat.completions.create,
                                         model=settings.MODEL_NAME,
                                         messages=[
                                             {"role": "system", "content": prompt},
                                             {"role": "user", "content": str(chat_history)}
                                         ],
                                         temperature=settings.MODEL_TEMPERATURE)

    return {
        "content": completion.choices[0].message.content,
        "usage": completion.usage
    }



