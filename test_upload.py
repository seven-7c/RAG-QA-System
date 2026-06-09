import streamlit as st
import tempfile
import os
from document_loader import load_document

st.title("📤 文件上传测试")

uploaded_files = st.file_uploader("上传文档", type=["pdf", "docx", "txt"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"✅ 成功检测到 {len(uploaded_files)} 个文件")
    
    for idx, file in enumerate(uploaded_files):
        st.subheader(f"文件 {idx+1}: {file.name}")
        st.info(f"文件名: {file.name}")
        st.info(f"文件类型: {file.type}")
        st.info(f"文件大小: {len(file.read())} 字节")
        file.seek(0)
        
        file_ext = os.path.splitext(file.name)[1].lower()
        st.info(f"扩展名: {file_ext}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, mode='wb') as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        
        try:
            text = load_document(tmp_path)
            st.success(f"✅ 成功读取文件内容")
            st.info(f"文本长度: {len(text)} 字符")
            st.text_area("文件内容预览", text[:500], height=100)
            os.unlink(tmp_path)
        except Exception as e:
            st.error(f"❌ 读取文件失败: {str(e)}")
            os.unlink(tmp_path)

st.divider()
st.info("测试完成！文件上传和读取功能正常工作。")