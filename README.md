# RAG智能问答系统

## 项目简介

本项目基于Ollama本地大模型、LangChain框架和Streamlit开发工具，构建了一个能够"学习"指定本地文档并回答相关问题的智能问答系统。系统支持PDF、DOCX、TXT等多种文档格式，能够自动进行文本分块、向量化存储和相似性检索，为用户提供基于文档内容的精准问答服务。

## 环境要求与安装步骤

### 系统要求
- Windows 10/11
- Python 3.10+
- Ollama

### 安装步骤

1. **安装Ollama**
   - 下载地址：https://ollama.com/download
   - 安装完成后，在命令行执行：`ollama pull deepseek-r1:7b`
   - 下载嵌入模型：`ollama pull nomic-embed-text`

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

## 使用说明

### 运行Web应用
```bash
streamlit run app.py
```

### 使用步骤
1. 在左侧侧边栏上传PDF、DOCX或TXT格式的文档
2. 点击"构建知识库"按钮处理文档
3. 在问答区输入问题并点击"提问"
4. 系统会基于文档内容进行回答
5. 如果文档中没有相关信息，会显示"文档中未找到相关答案"

### 命令行测试

测试Ollama连接：
```bash
python test_ollama.py
```

测试RAG系统：
```bash
python test_rag.py
```

## 关键技术点说明

### RAG流程
1. **文档加载**：支持PDF、DOCX、TXT等多种格式文档的解析
2. **文本分块**：使用RecursiveCharacterTextSplitter，chunk_size=1000，chunk_overlap=200
3. **向量化**：使用Ollama内置的nomic-embed-text嵌入模型
4. **向量存储**：使用Chroma向量数据库
5. **相似性检索**：根据查询返回最相关的3个文本块
6. **问答生成**：使用DeepSeek-R1-7B模型结合检索到的上下文进行回答

### 所用模型
- **主模型**：deepseek-r1:7b（DeepSeek R1 7B参数模型）
- **嵌入模型**：nomic-embed-text（Ollama内置嵌入模型）

### 核心组件
- **LangChain**：构建RAG问答链
- **Chroma**：向量数据库
- **Streamlit**：Web界面开发
- **Ollama**：本地大模型部署

## 项目结构

```
RAG-QA-System/
├── app.py                 # Streamlit Web应用主文件
├── config.py              # 配置文件
├── document_loader.py     # 文档加载与向量数据库管理
├── rag_chain.py           # RAG问答链实现
├── test_ollama.py         # Ollama连接测试
├── test_rag.py            # RAG系统测试
├── requirements.txt       # 依赖包列表
├── .gitignore             # Git忽略配置
├── documents/             # 示例文档目录
│   ├── nlp_intro.txt
│   ├── transformer.txt
│   ├── bert.txt
│   ├── word2vec.txt
│   └── gpt.txt
└── chroma_db/             # 向量数据库目录（运行时生成）
```

## 功能特点

- ✅ 支持多格式文档上传（PDF、DOCX、TXT）
- ✅ 自动构建向量知识库
- ✅ 基于文档内容的精准问答
- ✅ 对话历史记录与上下文记忆
- ✅ 知识库状态实时显示
- ✅ 支持清空知识库重新构建
- ✅ 对无关问题正确拒答（显示"文档中未找到相关答案"）

## 问答示例

### 相关问题
**问**: 什么是自然语言处理？
**答**: 自然语言处理（Natural Language Processing，NLP）是人工智能领域的一个重要分支，致力于使计算机能够理解、解释和生成人类语言。

**问**: Transformer模型的主要特点是什么？
**答**: Transformer的主要特点包括：1. 自注意力机制；2. 多头注意力；3. 位置编码；4. 编码器-解码器结构；5. 残差连接和层归一化。

### 无关问题
**问**: 如何制作蛋糕？
**答**: 文档中未找到相关答案

## 打包成EXE

使用PyInstaller打包：
```bash
pyinstaller --onefile --windowed app.py
```

打包后的exe文件位于`dist/`目录下。

## 已知问题与改进方向

### 已知问题
- 大文件处理时间较长
- 某些PDF文件可能存在解析问题

### 改进方向
- 支持更多文档格式（如Markdown、HTML）
- 增加文档预览功能
- 支持批量文档上传
- 添加夜间模式
- 支持问答记录导出

## 许可证

MIT License