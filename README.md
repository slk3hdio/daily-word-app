# Daily Word App

## 项目简介
本项目用于 QQ-Bot-New 项目的 daily_word 插件后端，提供单词学习相关的 API 服务。

## 功能特性
- 提供英语单词的详细信息，包括：
  - 英式和美式发音
  - 词性和释义
  - 单词标签分类
- 支持用户进度跟踪
- 提供单词听写功能

## 技术栈
- Python
- MySQL
- Flask (Web框架)

## 项目结构
```plaintext
daily-word-app/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用初始化
│   ├── routes.py          # API路由
│   ├── database.py        # 数据库操作
│   ├── word.py            # 单词模型
│   └── user.py            # 用户模型
├── data/                   # 数据文件
│   ├── words.txt          # 单词基础数据
│   └── pronounciation*.txt # 发音数据文件
├── script/                 # 数据处理脚本
│   ├── format.py          # 数据格式化
│   ├── load_words.py      # 单词数据导入
│   └── load_pronounciation.py # 发音数据导入
└── test/                   # 测试目录
    └── test.py            # 测试用例
```
