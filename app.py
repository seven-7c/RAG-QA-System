import streamlit as st
import os
import tempfile
from document_loader import load_document, build_vector_db, get_retriever, query_similar_documents
from rag_chain import build_rag_chain, get_answer
from config import VECTOR_DB_PATH, DOCUMENTS_FOLDER

st.set_page_config(page_title="RAG智能问答系统", page_icon="📚", layout="wide")

def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = None
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False
    if "chunk_count" not in st.session_state:
        st.session_state.chunk_count = 0

def count_chunks():
    if os.path.exists(VECTOR_DB_PATH):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
            collections = client.list_collections()
            if collections:
                collection = client.get_collection(collections[0].name)
                return collection.count()
        except:
            return 0
    return 0

init_session_state()

st.title("📚 RAG智能问答系统")

with st.sidebar:
    st.header("知识库管理")
    
    uploaded_files = st.file_uploader(
        "上传文档",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    
    if st.button("📥 构建知识库"):
        if uploaded_files:
            with st.spinner("正在处理文档..."):
                documents = []
                filenames = []
                
                for uploaded_file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    
                    try:
                        text = load_document(tmp_path)
                        if text.strip():
                            documents.append(text)
                            filenames.append(uploaded_file.name)
                            st.session_state.uploaded_files.append(uploaded_file.name)
                        os.unlink(tmp_path)
                    except Exception as e:
                        st.error(f"处理 {uploaded_file.name} 失败: {e}")
                        os.unlink(tmp_path)
                
                if documents:
                    build_vector_db(documents, filenames)
                    st.session_state.db_initialized = True
                    st.session_state.chunk_count = count_chunks()
                    st.success(f"成功处理 {len(documents)} 份文档")
                    st.session_state.rag_chain = build_rag_chain()
                else:
                    st.warning("没有成功加载任何文档")
        else:
            st.warning("请先上传文档")
    
    if st.button("🗑️ 清空知识库"):
        import shutil
        if os.path.exists(VECTOR_DB_PATH):
            shutil.rmtree(VECTOR_DB_PATH)
            st.session_state.db_initialized = False
            st.session_state.rag_chain = None
            st.session_state.chat_history = []
            st.session_state.chunk_count = 0
            st.success("知识库已清空")
    
    st.divider()
    
    st.subheader("知识库状态")
    st.info(f"已加载文档: {len(st.session_state.uploaded_files)} 份")
    st.info(f"文本块数量: {st.session_state.chunk_count} 个")
    
    if st.session_state.db_initialized:
        st.success("✅ 知识库已就绪")
    else:
        st.warning("⚠️ 知识库尚未构建")

col1, col2 = st.columns([3, 2])

with col1:
    st.header("问答交互")
    
    if st.session_state.db_initialized:
        user_question = st.text_input("请输入您的问题:", key="question_input")
        
        if st.button("提问"):
            if user_question.strip():
                with st.spinner("正在思考..."):
                    if st.session_state.rag_chain is None:
                        st.session_state.rag_chain = build_rag_chain()
                    
                    answer, sources = get_answer(
                        st.session_state.rag_chain,
                        user_question,
                        st.session_state.chat_history
                    )
                    
                    st.session_state.chat_history.append(("user", user_question))
                    st.session_state.chat_history.append(("assistant", answer))
                    
                    st.success("回答:")
                    st.write(answer)
                    
                    if sources and "文档中未找到相关答案" not in answer:
                        st.subheader("参考来源")
                        for i, source in enumerate(sources, 1):
                            st.caption(f"{i}. {source.metadata.get('source', '未知')}")
            else:
                st.warning("请输入问题")
    else:
        st.info("请先在左侧上传文档并构建知识库")
    
    st.divider()
    st.header("对话历史")
    
    if st.session_state.chat_history:
        for role, content in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"**您:** {content}")
            else:
                st.markdown(f"**助手:** {content}")
    else:
        st.info("暂无对话记录")

with col2:
    st.header("📖 知识库文档")
    
    if st.session_state.uploaded_files:
        for filename in st.session_state.uploaded_files:
            st.write(f"- {filename}")
    else:
        st.info("暂无文档")
    
    st.divider()
    st.header("💡 使用说明")
    st.markdown("""
    1. 在左侧上传PDF、DOCX或TXT格式的文档
    2. 点击"构建知识库"按钮处理文档
    3. 在问答区输入问题并点击"提问"
    4. 系统会基于文档内容进行回答
    5. 如果文档中没有相关信息，会显示"文档中未找到相关答案"
    """)
    
    st.divider()
    st.header("技术说明")
    st.markdown("""
    - **模型**: DeepSeek-R1-7B
    - **嵌入模型**: nomic-embed-text
    - **向量数据库**: Chroma
    - **文本分块**: chunk_size=1000, chunk_overlap=200
    """)