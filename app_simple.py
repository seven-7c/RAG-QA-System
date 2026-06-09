import streamlit as st
import os
import tempfile

st.set_page_config(page_title="RAG智能问答系统", page_icon="📚", layout="wide")

def init_session_state():
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False

def load_document(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        from PyPDF2 import PdfReader
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif ext == ".docx":
        import docx
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

init_session_state()

st.title("📚 RAG智能问答系统")

with st.sidebar:
    st.header("知识库管理")
    
    uploaded_files = st.file_uploader(
        "上传文档",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    if uploaded_files:
        st.success(f"✅ 已选择 {len(uploaded_files)} 个文件")
        for file in uploaded_files:
            st.info(f"- {file.name} ({len(file.read())} 字节)")
            file.seek(0)
    
    if st.button("📥 构建知识库"):
        if uploaded_files:
            with st.spinner("正在处理文档..."):
                processed_count = 0
                for uploaded_file in uploaded_files:
                    file_name = uploaded_file.name
                    file_ext = os.path.splitext(file_name)[1].lower()
                    
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, mode='wb') as tmp:
                            tmp.write(uploaded_file.read())
                            tmp_path = tmp.name
                        
                        text = load_document(tmp_path)
                        os.unlink(tmp_path)
                        
                        if text.strip():
                            if file_name not in st.session_state.uploaded_files:
                                st.session_state.uploaded_files.append(file_name)
                            processed_count += 1
                            st.success(f"✅ 成功处理: {file_name}")
                        else:
                            st.warning(f"文件内容为空: {file_name}")
                    
                    except Exception as e:
                        st.error(f"处理 {file_name} 失败: {str(e)}")
                
                if processed_count > 0:
                    st.session_state.db_initialized = True
                    st.success(f"🎉 成功构建知识库，共 {processed_count} 份文档")
                else:
                    st.warning("没有成功加载任何文档")
        else:
            st.warning("请先上传文档")
    
    if st.button("🗑️ 清空知识库"):
        st.session_state.uploaded_files = []
        st.session_state.db_initialized = False
        st.success("知识库已清空")
    
    st.divider()
    st.subheader("知识库状态")
    st.info(f"已加载文档: {len(st.session_state.uploaded_files)} 份")
    if st.session_state.db_initialized:
        st.success("✅ 知识库已就绪")
    else:
        st.warning("⚠️ 知识库尚未构建")

st.header("问答交互")
if st.session_state.db_initialized:
    st.success("✅ 知识库已构建完成，可以开始提问")
    user_question = st.text_input("请输入您的问题:")
    if st.button("提问"):
        if user_question.strip():
            st.info(f"您的问题: {user_question}")
            st.warning("⚠️ Ollama服务未安装，问答功能需要Ollama支持")
        else:
            st.warning("请输入问题")
else:
    st.info("请先在左侧上传文档并构建知识库")

st.divider()
st.header("📖 已上传的文档")
if st.session_state.uploaded_files:
    for filename in st.session_state.uploaded_files:
        st.write(f"- {filename}")
else:
    st.info("暂无文档")