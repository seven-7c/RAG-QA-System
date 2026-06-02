from langchain_community.chat_models import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from document_loader import get_retriever
from config import MODEL_NAME, TOP_K

SYSTEM_PROMPT = """
你是一个专业的文档问答助手。你的任务是基于提供的参考文档来回答用户的问题。

规则：
1. 仔细阅读并理解提供的参考文档内容。
2. 只使用文档中的信息来回答问题，不要添加任何外部知识。
3. 如果文档中没有相关信息，请明确说"文档中未找到相关答案"。
4. 回答要简洁明了，直接针对问题。
5. 保持回答的准确性和客观性。

参考文档：
{context}

问题：
{question}

回答：
"""

def build_rag_chain():
    llm = ChatOllama(model=MODEL_NAME, temperature=0)
    
    retriever = get_retriever(k=TOP_K)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=SYSTEM_PROMPT
    )
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        verbose=False
    )
    
    return chain

def get_answer(chain, question, chat_history=[]):
    result = chain({
        "question": question,
        "chat_history": chat_history
    })
    return result["answer"], result["source_documents"]