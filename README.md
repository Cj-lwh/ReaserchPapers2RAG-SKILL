# 文献转 RAG 知识库

<p align="center">
  <strong>将你的研究文献库转换为可被ClaudeCode语义检索的本地知识库</strong>
</p>

<p align="center">
  <a href="#功能特点">功能特点</a> •
  <a href="#安装说明">安装说明</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#使用方法">使用方法</a>
</p>

---

## 项目简介

**文献转 RAG 知识库** 想给ClaudeCode外接一个文献知识库，让它辅佐你做科研，但是文献数量太多了喂不下？ReaserPaper2RAG/skill是一个轻量级运行的RAG解决方案，将你文献库中的 PDF 和 Word 文档转换为语义检索知识库。使用自然语言查询你的文献库——无需云服务、无需 API 费用、数据完全本地化。

## 功能特点

| 功能 | 说明 |
|------|------|
| **多格式支持** | 支持 PDF 和 Word 文档（.pdf, .docx, .doc） |
| **语义检索** | 基于 FAISS 的向量检索，支持多语言嵌入 |
| **交互模式** | 提供命令行交互式查询界面 |
| **离线运行** | 无需 API 密钥，完全本地运行 |
| **国内优化** | 自动选择国内镜像，解决网络问题 |
| **Zotero Endnote兼容** | 告诉它文献库文件夹在哪里，或让它自动检测 |

## 安装说明

### 环境要求

- Python 3.8 或更高版本

### 安装步骤

**第一步：下载项目**

```bash
git clone https://github.com/yourusername/research-papers-to-rag.git
cd research-papers-to-rag
```

**第二步：安装依赖**

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 提取文档文本

```bash
python scripts/extract_documents.py /path/to/your/papers
```

**输出示例：**
```
Found 25 PDF files, 5 Word files
Processing [1/30]: research_paper.pdf
...
Successfully extracted 30 documents

Statistics:
  PDF documents: 25
  Word documents: 5
  Total characters: 2,345,678
```

### 2. 构建向量索引

```bash
python scripts/build_vector_store.py
```

**输出示例：**
```
Loading embedding model...
Created 1,234 text chunks
Built index with 1,234 vectors
Saved to ~/.literature_kb
```

### 3. 检索文献

```bash
python scripts/search.py "你的查询内容"
```

## 使用方法

### 单次查询

```bash
python scripts/search.py "查询内容"
python scripts/search.py "深度学习" -k 10    # 返回前 10 条结果
```

### 交互模式

```bash
python scripts/search.py -i
```

```
============================================================
文献知识库 - 交互式查询
============================================================
输入查询内容进行检索，输入 'quit' 或 'exit' 退出
输入 'list' 查看所有文档
------------------------------------------------------------

查询> 深度学习图像分类

============================================================
查询: 深度学习图像分类
找到 5 个相关片段
============================================================

[1] research_paper.pdf
    相关性: 82.34%
    内容预览:
    本文综述了深度学习在图像分类领域的应用...
```

### 列出所有文档

```bash
python scripts/search.py --list
```

## 命令参考

| 命令 | 功能 |
|------|------|
| `search.py "查询"` | 检索相关文献片段 |
| `search.py "查询" -k N` | 返回前 N 条结果 |
| `search.py --list` | 列出知识库中所有文档 |
| `search.py -i` | 进入交互查询模式 |
| `extract_documents.py 路径` | 提取文档文本 |
| `build_vector_store.py` | 构建向量索引 |

## 技术细节

| 组件 | 技术方案 |
|------|---------|
| **PDF 解析** | PyMuPDF (fitz) |
| **Word 解析** | python-docx |
| **嵌入模型** | paraphrase-multilingual-MiniLM-L12-v2 |
| **向量维度** | 384 |
| **向量存储** | FAISS (IndexFlatIP) |
| **存储位置** | ~/.literature_kb/ |
| **镜像源** | 自动选择国内镜像或官方源 |

## 更新知识库

```bash
# 添加新文档到文献文件夹后，重新执行：
python scripts/extract_documents.py /path/to/documents
python scripts/build_vector_store.py
```

## 项目结构

```
research-papers-to-rag/
├── SKILL.md                 # Skill 定义文件
├── README.md                # 使用说明
├── requirements.txt         # Python 依赖
└── scripts/
    ├── extract_documents.py     # 文档提取
    ├── build_vector_store.py    # 向量索引构建
    └── search.py                # 检索工具
```

## 许可证

MIT License

---

*为需要在本地检索文献库的研究者而构建*