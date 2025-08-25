import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from model_localizer import download_model_to_local

def build_vectorstore(file_path, persist_dir):
    """
    加载文档，进行文本分块和向量化，构建或加载向量数据库
    :param file_path: 文档文件路径
    :param persist_dir: 向量数据库持久化目录
    :return: 向量数据库对象
    """
    # 下载或使用本地模型
    local_model_path = download_model_to_local()
    
    # 读文件转为documents对象
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    # 文本分块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？"]
    )
    texts = text_splitter.split_documents(documents)

    # 向量化 - 使用本地化的轻量级中文模型
    embeddings = HuggingFaceEmbeddings(
        model_name=local_model_path,
        encode_kwargs={'normalize_embeddings': True},
        model_kwargs={'device': 'cpu'}
    )

    # 检查是否已存在向量数据库
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        # 已存在，直接加载
        print("加载已存在的向量数据库...")
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_dir
        )
    else:
        # 不存在，构建新的向量数据库
        print("构建新的向量数据库...")
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        # 持久化保存
        vectorstore.persist()
    return vectorstore    