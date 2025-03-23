from typing import List
import csv
from pathlib import Path
from tqdm import tqdm

def load_tags(tags_file: Path) -> List[str]:
    """从CSV文件加载标签列表"""
    tags_list = []
    
    with open(tags_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tags_list.append(row["name"])
    
    return tags_list

def get_system_prompt() -> str:
    """获取系统提示词"""
    return """你是一个稳定扩散模型的标签分类助手，专注于对标签进行安全评级。你需要将输入的标签分类为以下四种之一，并且给出中文解释和翻译：
    - general: 通用内容，适合所有年龄段
    - sensitive: 敏感内容，可能不适合未成年人
    - nsfw: 露三点，露敏感器官
    - explicit: 明确包含色情、性交等内容
    
    具体来说，像露三点的级别，就是nsfw，sensitive最多是擦边但不露点的，explicit是属于涉及到性交的
    注意不要把一些不露点的都分到nsfw里去了，如果只是什么蕾丝边胸罩之类的内衣，最多分到sensitive。
    nsfw的必须是露三点，露敏感器官的才可以。
    同时禁止过度解读，比如hand_under_clothes这种标签，你不能发散为性暗示行为，不能分为nsfw，标签没体现就不要随便发散

    你的输出必须包含：
    - "category": 一个字符串，表示标签属于什么分类。
    - "explanation": 对分类结果的详细中文解释，说明为什么内容属于该分类。
    - "translation": 标签的中文翻译。
    
    保持分类的准确性，请谨慎处理边界情况。尽可能识别出标签中可能存在的敏感元素。
    请提供准确的中文翻译。"""

def format_progress(completed: int, total: int, elapsed: float) -> str:
    """格式化进度信息"""
    progress = completed / total
    eta = (elapsed / completed) * (total - completed) if completed > 0 else 0
    return f"进度: {completed}/{total} ({progress:.1%}), 预计剩余时间: {eta:.1f}秒" 