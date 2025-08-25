import asyncio
import json
import redis
import logging
import uuid

from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from config import settings
from .chat_processor import process_multi_turn_chat, build_chat_history
from .llm_client import get_llm_client
from chroma_db_tools.model_localizer import download_model_to_local
# from .kafka_tool import KafkaProducerTool

class ChatService:
    def __init__(self):
        if not settings.REDIS_PASSWORD:
            print("Please set REDIS_PASSWORD environment variable.")
        self.redis_client = redis.from_url(
            url=settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        if not settings.API_KEY or not settings.BASE_URL:
            print("Please set API_KEY and BASE_URL environment variables.")
        self.llm_client = get_llm_client(
            base_url=settings.BASE_URL,
            api_key=settings.API_KEY
        )
        # self.kafka_producer = KafkaProducerTool(
        #     bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        #     topic=settings.KAFKA_TOPIC
        # )
        # 向量化 - 使用本地化的轻量级中文模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name=download_model_to_local(),
            encode_kwargs={'normalize_embeddings': True},
            model_kwargs={'device': 'cpu'}
        )

    async def process_chat(self, question: str, session_id: str, api_key: str) -> str:
        """
        处理用户对话
        :param question: 用户问题
        :param session_id: 会话ID
        :param api_key: API KEY
        :return: 模型输出
        """
        chroma_db_dir = self.get_chroma_db(api_key)
        # 从持久化目录加载向量数据库对象
        vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory=chroma_db_dir
        )

        # 获取用户对话历史
        chat_history = self.get_chat_history(session_id)
        # 构建本轮用户对话
        cur_chat = build_chat_history("user", question)
        # 添加本轮对话进对话历史
        chat_history.append(cur_chat)

        # 处理多轮对话
        logging.debug(f"准备处理对话{session_id}-{chat_history}")
        tasks = [
            process_multi_turn_chat(chat_history, vectorstore, self.llm_client)
        ]
        result_ft = await asyncio.gather(*tasks)

        # 更新Redis中的会话历史
        self.update_chat_history(
            session_id=session_id,
            question_chat=cur_chat,
            result_chat=build_chat_history("bot", result_ft[0]['content']),
            index=len(chat_history)
        )

        # # 推送计费结果到消息队列
        # self.kafka_producer.send_message({
        #     "usage": result_ft[0]['usage'],
        #     "api_key": settings.API_KEY
        # })
 
        return result_ft[0]['content']

    def get_chat_history(self, session_id: str) -> list:
        """
        构建用户对话历史
        :param session_id: 会话ID
        :return: 用户对话历史
        """
        # 获取历史对话
        session_data = self.redis_client.hgetall(f"session:{session_id}")
        if not session_data:
            messages = []
        else:
            # 提取字段名，并提取数字部分进行排序
            sorted_fields = sorted(session_data.keys(),
                                   key=lambda k: int(k.split('_')[1]))

            messages = []
            for field in sorted_fields:
                # 解析每个JSON字符串
                message_data = json.loads(session_data[field])
                messages.append(message_data)

        return messages

    def update_chat_history(self, session_id: str, question_chat: dict, result_chat: dict, index: int = 0) -> None:
        """
        更新Redis中的会话历史
        :param session_id: 会话ID
        :param question_chat: 用户输入
        :param result_chat: 模型输出
        :param index: 索引
        """
        # TODO：TTL
        self.redis_client.hset(
            f"session:{session_id}",
            f"message_{index}",
            json.dumps(question_chat)
        )
        self.redis_client.hset(
            f"session:{session_id}",
            f"message_{index + 1}",
            json.dumps(result_chat)
        )

    def get_chroma_db(self, api_key: str) -> str:
        """
        根据API KEY获取对应的向量数据库
        :param api_key: API KEY
        :return: 向量数据库路径
        """
        # TODO
        logging.debug(f"根据API KEY获取对应的向量数据库{api_key}")
        return "/chroma_db/chroma_db_demo1"

    @staticmethod
    def generate_session_id() -> str:
        """
        生成会话ID
        :return: 会话ID
        """
        return f"session_{str(uuid.uuid4())}"





