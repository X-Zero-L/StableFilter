from typing import Literal, Dict, List, Optional
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel, Field
from config import config
from client import openai_client
import csv
import os
import json
import asyncio
import time
from datetime import datetime

model = OpenAIModel(config.openai_model, openai_client=openai_client)


class LabelResult(BaseModel):
    category: Literal["general", "sensitive", "nsfw", "explicit"] = Field(
        ..., description="分类标签, 可选值: general, sensitive, nsfw, explicit"
    )
    explanation: str = Field(..., description="对分类结果的详细解释说明")
    translation: str = Field(..., description="标签的中文翻译")


class TagClassification(BaseModel):
    tag: str
    result: LabelResult
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ClassificationResults(BaseModel):
    results: Dict[str, TagClassification] = {}
    
    def add_result(self, tag: str, result: LabelResult):
        self.results[tag] = TagClassification(tag=tag, result=result)
    
    def save(self, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, filename: str) -> "ClassificationResults":
        if not os.path.exists(filename):
            return cls()
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls.parse_obj(data)
        except Exception as e:
            print(f"加载文件 {filename} 时出错: {e}")
            return cls()


agent = Agent(model, result_type=LabelResult)


# 加载标签数据
def load_tags() -> List[str]:
    tags_list = []
    tags_file = os.path.join(os.path.dirname(__file__), "selected_tags.csv")

    with open(tags_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tags_list.append(row["name"])
    
    return tags_list


# 系统提示词：告诉模型它的任务和规则
@agent.system_prompt
async def system_prompt():
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
    - "explanation": 对分类结果的详细解释，说明为什么内容属于该分类。
    - "translation": 标签的中文翻译。
    
    保持分类的准确性，请谨慎处理边界情况。尽可能识别出标签中可能存在的敏感元素。
    请提供准确的中文翻译。"""


# 处理单个标签
async def process_tag(tag_name: str, results: ClassificationResults, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            print(f"正在处理标签: {tag_name}")
            result = await agent.run(tag_name)
            
            # 只添加结果，不保存
            results.add_result(tag_name, result.data)
            
            print(f"标签 {tag_name} 处理完成: {result.data.category} - {result.data.translation}")
            return tag_name, result.data
        except Exception as e:
            print(f"处理标签 {tag_name} 时出错: {e}")
            return tag_name, None


# 主函数
async def main():
    # 设置并发数
    max_concurrency = 100
    
    # 结果文件路径
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    results_file = os.path.join(results_dir, "tag_classifications.json")
    
    # 加载已有结果
    results = ClassificationResults.load(results_file)
    
    # 加载所有标签
    all_tags = load_tags()
    print(f"从CSV加载了 {len(all_tags)} 个标签")
    print(f"已有 {len(results.results)} 个标签处理结果")
    
    # 找出未处理的标签
    tags_to_process = [tag for tag in all_tags if tag not in results.results]
    print(f"需要处理 {len(tags_to_process)} 个标签")
    
    if not tags_to_process:
        print("没有需要处理的标签，程序退出")
        return
    
    # 创建信号量控制并发
    semaphore = asyncio.Semaphore(max_concurrency)
    
    # 创建任务
    tasks = []
    for tag in tags_to_process:
        tasks.append(process_tag(tag, results, semaphore))
    
    # 执行任务并显示进度
    total = len(tasks)
    completed = 0
    save_counter = 0
    save_interval = 100  # 每处理100个标签保存一次
    start_time = time.time()
    
    for future in asyncio.as_completed(tasks):
        tag_name, result = await future
        completed += 1
        save_counter += 1
        
        # 每处理save_interval个标签保存一次
        if save_counter >= save_interval:
            print(f"已处理 {completed} 个标签，保存结果...")
            results.save(results_file)
            save_counter = 0
        
        # 计算进度和预估剩余时间
        elapsed = time.time() - start_time
        progress = completed / total
        eta = (elapsed / completed) * (total - completed) if completed > 0 else 0
        
        print(f"进度: {completed}/{total} ({progress:.1%}), 预计剩余时间: {eta:.1f}秒")
    
    # 统计结果
    categories = {}
    for tag, classification in results.results.items():
        category = classification.result.category
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    print("\n处理完成，分类统计:")
    for category, count in sorted(categories.items()):
        print(f"  - {category}: {count} 个标签")
    
    # 最后再保存一次
    results.save(results_file)
    print("所有结果已保存")


# 运行主程序
if __name__ == "__main__":
    import asyncio
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已中断")
        # 尝试保存当前结果
        try:
            results_dir = os.path.join(os.path.dirname(__file__), "results")
            results_file = os.path.join(results_dir, "tag_classifications.json")
            if os.path.exists(results_file):
                results = ClassificationResults.load(results_file)
                results.save(f"{results_file}.interrupted.{int(time.time())}")
                print("已在中断时保存当前结果")
        except Exception as e:
            print(f"中断时保存结果出错: {e}")
    except Exception as e:
        print(f"程序出错: {e}")
        import traceback
        traceback.print_exc()
