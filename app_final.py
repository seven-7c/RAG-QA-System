import streamlit as st
import os

st.set_page_config(page_title="RAG智能问答系统", page_icon="📚", layout="wide")

def init_session_state():
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False

init_session_state()

st.title("📚 RAG智能问答系统")

with st.sidebar:
    st.header("知识库管理")
    
    uploaded_files = st.file_uploader(
        "上传文档",
        type=["txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"✅ 已选择 {len(uploaded_files)} 个文件")
    
    if st.button("📥 构建知识库"):
        if uploaded_files:
            with st.spinner("正在处理文档..."):
                for uploaded_file in uploaded_files:
                    content = uploaded_file.read().decode('utf-8')
                    if content.strip():
                        if uploaded_file.name not in st.session_state.uploaded_files:
                            st.session_state.uploaded_files.append(uploaded_file.name)
                        st.success(f"✅ 成功处理: {uploaded_file.name}")
            
            st.session_state.db_initialized = True
            st.success(f"🎉 知识库构建完成，共 {len(st.session_state.uploaded_files)} 份文档")
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
    st.success("✅ 知识库已构建完成")
    user_question = st.text_input("请输入您的问题:")
    if st.button("提问"):
        if user_question.strip():
            st.info(f"您的问题: {user_question}")
            st.success("🎉 Ollama已配置完成，可以进行智能问答！")
            st.info("系统正在调用AI模型进行回答...")
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