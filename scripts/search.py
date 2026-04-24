"""
文献知识库查询工具
快速检索你的文献向量数据库

使用方法:
    python search.py "查询内容"
    python search.py "深度学习" -k 5
    python search.py --list                    # 列出所有文档
    python search.py --interactive             # 交互模式
"""
import argparse
import pickle
import os
import sys
from pathlib import Path

# 设置 Hugging Face 镜像（优先国内镜像，失败则回退）
def setup_hf_mirror():
    """设置 Hugging Face 镜像源"""
    mirrors = [
        ('https://hf-mirror.com', '国内镜像'),
        ('https://huggingface.co', '官方源'),
    ]

    for url, name in mirrors:
        os.environ['HF_ENDPOINT'] = url
        try:
            import urllib.request
            urllib.request.urlopen(f"{url}/", timeout=5)
            return url
        except:
            continue

    # 默认使用国内镜像
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    return 'https://hf-mirror.com'

# 初始化镜像
setup_hf_mirror()

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 延迟加载模型，只在需要时加载
_model = None
_index = None
_documents = None
_metadata = None

STORE_DIR = Path.home() / '.literature_kb'


def load_index():
    """加载向量索引和数据"""
    global _index, _documents, _metadata

    if _index is None:
        index_path = STORE_DIR / 'index.faiss'
        data_path = STORE_DIR / 'data.pkl'

        if not index_path.exists():
            print(f"错误: 向量索引不存在: {index_path}")
            print("请先运行 build_vector_store.py 构建向量库")
            sys.exit(1)

        import faiss
        _index = faiss.read_index(str(index_path))

        with open(data_path, 'rb') as f:
            data = pickle.load(f)
            _documents = data['documents']
            _metadata = data['metadata']

    return _index, _documents, _metadata


def load_model():
    """加载嵌入模型（延迟加载）"""
    global _model
    if _model is None:
        print("加载嵌入模型中...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("模型加载完成")
    return _model


def search(query: str, k: int = 5):
    """
    检索相关文献

    Args:
        query: 查询文本
        k: 返回结果数量
    """
    index, documents, metadata = load_index()
    model = load_model()

    # 编码查询
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # 搜索
    scores, indices = index.search(query_embedding.astype('float32'), k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(documents):
            results.append({
                'content': documents[idx],
                'metadata': metadata[idx],
                'score': float(scores[0][i])
            })

    return results


def list_documents():
    """列出所有文档"""
    _, _, metadata = load_index()

    seen_files = set()
    documents = []

    for meta in metadata:
        filename = meta.get('filename', '')
        if filename and filename not in seen_files:
            seen_files.add(filename)
            documents.append({
                'filename': filename,
                'title': meta.get('title', ''),
                'author': meta.get('author', ''),
                'file_type': meta.get('file_type', ''),
            })

    return documents


def print_search_results(query: str, results: list):
    """格式化打印检索结果"""
    print(f"\n{'='*60}")
    print(f"查询: {query}")
    print(f"找到 {len(results)} 个相关片段")
    print('='*60)

    for i, r in enumerate(results, 1):
        meta = r['metadata']
        print(f"\n[{i}] {meta.get('filename', 'Unknown')}")
        if meta.get('title'):
            print(f"    标题: {meta['title']}")
        if meta.get('author'):
            print(f"    作者: {meta['author']}")
        print(f"    相关性: {r['score']:.2%}")
        print(f"    内容预览:")
        content = r['content'][:300] + "..." if len(r['content']) > 300 else r['content']
        print(f"    {content}")


def print_document_list(documents: list):
    """格式化打印文档列表"""
    print(f"\n{'='*60}")
    print(f"知识库文档列表 (共 {len(documents)} 篇)")
    print('='*60)

    for i, doc in enumerate(documents, 1):
        print(f"\n{i}. {doc['filename']}")
        if doc['title']:
            print(f"   标题: {doc['title']}")
        if doc['author']:
            print(f"   作者: {doc['author']}")


def interactive_mode():
    """交互式查询模式"""
    print("\n" + "="*60)
    print("文献知识库 - 交互式查询")
    print("="*60)
    print("输入查询内容进行检索，输入 'quit' 或 'exit' 退出")
    print("输入 'list' 查看所有文档")
    print("-"*60)

    # 预加载模型
    load_model()

    while True:
        try:
            query = input("\n查询> ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("再见!")
                break

            if query.lower() == 'list':
                docs = list_documents()
                print_document_list(docs)
                continue

            results = search(query)
            print_search_results(query, results)

        except KeyboardInterrupt:
            print("\n再见!")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='文献知识库查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python search.py "深度学习"
    python search.py "machine learning" -k 10
    python search.py --list
    python search.py -i
        """
    )
    parser.add_argument('query', nargs='?', help='查询内容')
    parser.add_argument('-k', '--top-k', type=int, default=5, help='返回结果数量 (默认: 5)')
    parser.add_argument('--list', action='store_true', help='列出所有文档')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.list:
        docs = list_documents()
        print_document_list(docs)
    elif args.query:
        results = search(args.query, args.top_k)
        print_search_results(args.query, results)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
