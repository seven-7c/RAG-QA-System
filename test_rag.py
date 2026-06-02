import os
from document_loader import load_documents_from_folder, build_vector_db
from rag_chain import build_rag_chain, get_answer
from config import DOCUMENTS_FOLDER, VECTOR_DB_PATH

def test_rag_system():
    if not os.path.exists(DOCUMENTS_FOLDER):
        print(f"文档文件夹 {DOCUMENTS_FOLDER} 不存在，请先添加文档")
        return
    
    print("正在加载文档...")
    documents, filenames = load_documents_from_folder(DOCUMENTS_FOLDER)
    print(f"成功加载 {len(documents)} 份文档")
    
    print("正在构建向量数据库...")
    build_vector_db(documents, filenames)
    print("向量数据库构建完成")
    
    print("正在构建RAG问答链...")
    chain = build_rag_chain()
    print("RAG问答链构建完成")
    
    test_questions = [
        "什么是自然语言处理？",
        "Transformer模型的主要特点是什么？",
        "BERT模型是如何工作的？",
        "词向量的作用是什么？",
        "什么是预训练模型？",
        "量子计算的基本原理是什么？",
        "如何制作蛋糕？"
    ]
    
    print("\n开始测试问答功能...")
    for i, question in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {question}")
        answer, sources = get_answer(chain, question)
        print(f"回答: {answer}")
        if sources:
            print("参考来源:")
            for j, source in enumerate(sources, 1):
                print(f"  {j}. {source.metadata.get('source', '未知')}")

if __name__ == "__main__":
    test_rag_system()