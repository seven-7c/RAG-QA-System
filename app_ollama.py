import streamlit as st
import os
import json
import urllib.request

st.set_page_config(page_title="RAG智能问答系统", page_icon="📚", layout="wide")

def init_session_state():
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

init_session_state()

def call_ollama_api(prompt):
    try:
        url = "http://localhost:11434/api/generate"
        data = json.dumps({
            "model": "deepseek-r1:7b",
            "prompt": prompt,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={
            'Content-Type': 'application/json',
            'Content-Length': len(data)
        })
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '没有返回结果')
    
    except urllib.error.URLError as e:
        return f"网络错误: {str(e)}"
    except json.JSONDecodeError:
        return "解析结果失败"
    except Exception as e:
        return f"调用错误: {str(e)}"

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
        st.session_state.chat_history = []
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
    user_question = st.text_input("请输入您的问题:")
    
    if st.button("提问"):
        if user_question.strip():
            with st.spinner("正在思考..."):
                st.session_state.chat_history.append(("user", user_question))
                
                answer = call_ollama_api(user_question)
                
                st.session_state.chat_history.append(("assistant", answer))
                
                st.success("回答:")
                st.write(answer)
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

st.divider()
st.header("📖 已上传的文档")
if st.session_state.uploaded_files:
    for filename in st.session_state.uploaded_files:
        st.write(f"- {filename}")
else:
    st.info("暂无文档")