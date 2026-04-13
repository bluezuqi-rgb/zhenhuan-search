#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕索引生成器
将 subtitle_ollama.txt 转换为 index.json
"""

import json
import re
import os

# 配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
SUBTITLE_FILE = os.path.join(PROJECT_DIR, 'subtitle_ollama.txt')
OUTPUT_FILE = os.path.join(PROJECT_DIR, 'data', 'index.json')

def parse_subtitle_line(line):
    """解析单行字幕"""
    # 格式: E01_00_54 | 03:14 | 清康熙皇帝驾崩
    line = line.strip()
    if not line or line.startswith('#') or line.startswith('='):
        return None

    parts = line.split('|')
    if len(parts) < 3:
        return None

    filename = parts[0].strip()
    timestamp = parts[1].strip()
    text = parts[2].strip()

    # 跳过无字幕
    if text == '[无字幕]' or not text:
        return None

    # 解析集数和时间
    # E01_00_54 -> episode=1, time=00:54
    match = re.match(r'E(\d+)_(\d+)_(\d+)', filename)
    if not match:
        return None

    episode = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))

    # 截图文件名（去掉E前缀）
    image_filename = f"{episode:02d}_{minutes:02d}_{seconds:02d}.jpg"

    # 分词（简单按字符分割，过滤标点）
    keywords = extract_keywords(text)

    return {
        'id': filename,
        'episode': episode,
        'time': timestamp,
        'text': text,
        'image': image_filename,
        'keywords': keywords
    }

def extract_keywords(text):
    """提取关键词"""
    # 移除标点符号
    text = re.sub(r'[，。！？、；：""''（）【】《》\s]+', '', text)
    # 生成2-4字的词组
    keywords = set()
    for i in range(len(text)):
        for length in [2, 3, 4]:
            if i + length <= len(text):
                keywords.add(text[i:i+length])
    # 也添加单字
    for char in text:
        keywords.add(char)
    return list(keywords)

def build_index():
    """构建索引"""
    subtitles = []

    with open(SUBTITLE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            item = parse_subtitle_line(line)
            if item:
                subtitles.append(item)

    # 按集数和时间排序
    subtitles.sort(key=lambda x: (x['episode'], x['id']))

    # 统计信息
    episodes = set(item['episode'] for item in subtitles)
    print(f"解析完成:")
    print(f"  总记录数: {len(subtitles)}")
    print(f"  集数: {sorted(episodes)}")

    # 保存JSON
    output_data = {
        'total': len(subtitles),
        'episodes': sorted(list(episodes)),
        'subtitles': subtitles
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"索引已保存到: {OUTPUT_FILE}")
    print(f"文件大小: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")

if __name__ == '__main__':
    build_index()
