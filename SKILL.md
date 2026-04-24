---
name: research-papers-to-rag
description: |
  将研究文献（PDF 和 Word 文档）构建为可检索的知识库。当用户想要：
  - 从论文库创建可检索的知识库
  - 构建 RAG 向量数据库
  - 搜索和检索文献内容
  - 管理个人文献资料

  触发词："构建文献知识库", "创建RAG". "搜索我的文献", "文献检索", "论文知识库"
---

# 文献转 RAG 知识库

将你的研究文献（PDF 和 Word 文档）转换为可语义检索的知识库。

## 功能概述

1. **文档提取** - 从 PDF 和 Word 文档中提取文本
2. **向量索引** - 构建 FAISS 向量索引实现语义检索
3. **交互查询** - 用自然语言搜索你的文献库

## 环境要求

- Python 3.8+
- 依赖：`pymupdf`, `python-docx`, `sentence-transformers`, `faiss-cpu`

```bash
pip install -r requirements.txt
```

## 使用流程

### 步骤 1：指定文档路径

询问用户：
> "你的文献存放在哪里？请提供包含 PDF 或 Word 文档的文件夹路径(zotero文献库路径一般为安装目录下的/storage文件夹)。"

### 步骤 2：提取文档文本

```bash
python scripts/extract_documents.py /path/to/documents
```

### 步骤 3：构建向量索引

```bash
python scripts/build_vector_store.py
```

### 步骤 4：检索文献

使用 search.py 脚本检索：

```bash
python scripts/search.py "查询内容"
python scripts/search.py -i          # 交互模式
python scripts/search.py --list      # 列出所有文档
```

## 命令说明

| 命令 | 功能 |
|------|------|
| `search.py "查询"` | 检索相关文献片段 |
| `search.py "查询" -k 10` | 返回前 10 条结果 |
| `search.py --list` | 列出知识库中所有文档 |
| `search.py -i` | 进入交互查询模式 |

## 技术参数

- **嵌入模型：** `paraphrase-multilingual-MiniLM-L12-v2`（384 维）
- **向量存储：** FAISS（内积相似度）
- **支持格式：** PDF, DOCX, DOC
- **存储位置：** `~/.literature_kb/`
- **镜像源：** 自动选择国内镜像或官方源

## 文件结构

```
research-papers-to-rag/
├── SKILL.md
├── README.md
├── requirements.txt
└── scripts/
    ├── extract_documents.py   # 文档提取
    ├── build_vector_store.py  # 构建向量索引
    └── search.py              # 检索工具
```