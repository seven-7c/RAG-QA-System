import streamlit as st

st.title("文件上传测试")

uploaded_files = st.file_uploader("上传文档", type=["txt"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"已上传 {len(uploaded_files)} 个文件")
    
    for file in uploaded_files:
        content = file.read().decode('utf-8')
        st.write(f"文件名: {file.name}")
        st.write(f"内容: {content[:100]}...")
        st.success("✅ 文件上传成功!")

if st.button("测试按钮"):
    st.success("按钮点击成功!")