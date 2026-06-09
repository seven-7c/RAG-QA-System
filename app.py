import streamlit as st
import os
import tempfile
import subprocess
from document_loader import load_document, build_vector_db, get_retriever, query_similar_documents
from rag_chain import build_rag_chain, get_answer
from config import VECTOR_DB_PATH, DOCUMENTS_FOLDER, MODEL_NAME

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

def check_ollama_status():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, "Ollama服务正常运行"
        else:
            return False, f"Ollama命令执行失败: {result.stderr}"
    except FileNotFoundError:
        return False, "Ollama未安装，请先安装Ollama"
    except Exception as e:
        return False, f"检查Ollama状态失败: {str(e)}"

init_session_state()

ollama_available, ollama_msg = check_ollama_status()

st.title("📚 RAG智能问答系统")

if not ollama_available:
    st.warning(f"⚠️ {ollama_msg}")
    st.info("请先安装Ollama并运行 `ollama pull deepseek-r1:7b` 和 `ollama pull nomic-embed-text`")

with st.sidebar:
    st.header("知识库管理")
    
    uploaded_files = st.file_uploader(
        "上传文档",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    
    if st.button("📥 构建知识库"):
        if uploaded_files:
            st.info(f"检测到 {len(uploaded_files)} 个上传文件")
            with st.spinner("正在处理文档..."):
                documents = []
                filenames = []
                tmp_files = []
                
                try:
                    for idx, uploaded_file in enumerate(uploaded_files):
                        st.info(f"正在处理文件 {idx+1}/{len(uploaded_files)}: {uploaded_file.name}")
                        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                        file_bytes = uploaded_file.read()
                        file_size = len(file_bytes)
                        uploaded_file.seek(0)
                        st.info(f"文件大小: {file_size} 字节, 扩展名: {file_ext}")
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, mode='wb') as tmp:
                            tmp.write(file_bytes)
                            tmp_path = tmp.name
                            tmp_files.append(tmp_path)
                        
                        try:
                            text = load_document(tmp_path)
                            st.info(f"读取到文本长度: {len(text)} 字符")
                            if text.strip():
                                documents.append(text)
                                filenames.append(uploaded_file.name)
                                if uploaded_file.name not in st.session_state.uploaded_files:
                                    st.session_state.uploaded_files.append(uploaded_file.name)
                                st.success(f"✅ 成功处理: {uploaded_file.name}")
                            else:
                                st.warning(f"文件内容为空: {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"处理 {uploaded_file.name} 失败: {str(e)}")
                
                finally:
                    for tmp_path in tmp_files:
                        try:
                            if os.path.exists(tmp_path):
                                os.unlink(tmp_path)
                        except Exception as e:
                            st.warning(f"删除临时文件失败: {e}")
                
                st.info(f"成功解析 {len(documents)} 份文档")
                
                if documents:
                    st.session_state.db_initialized = True
                    st.session_state.chunk_count = sum(len(doc) // 1000 + 1 for doc in documents)
                    st.success(f"🎉 成功处理 {len(documents)} 份文档")
                    st.info(f"文件名: {', '.join(filenames)}")
                    
                    if ollama_available:
                        try:
                            st.info("正在构建向量数据库...")
                            build_vector_db(documents, filenames)
                            st.success("✅ 向量数据库构建成功")
                            st.session_state.chunk_count = count_chunks()
                            try:
                                st.session_state.rag_chain = build_rag_chain()
                                st.success("✅ RAG链构建成功")
                            except Exception as e:
                                st.warning(f"RAG链构建失败: {str(e)}")
                        except Exception as e:
                            st.error(f"构建知识库失败: {str(e)}")
                    else:
                        st.warning("⚠️ Ollama未安装，跳过向量数据库构建")
                else:
                    st.warning("没有成功加载任何文档")
        else:
            st.warning("请先上传文档")
    
    if st.button("📖 使用预置文档初始化"):
        with st.spinner("正在加载预置文档..."):
            try:
                from document_loader import load_documents_from_folder
                
                documents, filenames = load_documents_from_folder(DOCUMENTS_FOLDER)
                
                if documents:
                    build_vector_db(documents, filenames)
                    st.session_state.uploaded_files = filenames
                    st.session_state.db_initialized = True
                    st.session_state.chunk_count = count_chunks()
                    st.success(f"成功加载 {len(documents)} 份预置文档")
                    st.session_state.rag_chain = build_rag_chain()
                else:
                    st.warning("未找到预置文档")
            except Exception as e:
                st.error(f"加载预置文档失败: {str(e)}")
    
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