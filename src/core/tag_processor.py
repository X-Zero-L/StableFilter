import asyncio
import time
from typing import Optional, Tuple
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI

from src.models.tag_models import LabelResult, ClassificationResults
from src.config.settings import settings
from src.utils.tag_utils import get_system_prompt, load_tags, format_progress

class TagProcessor:
    """标签处理器"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key,base_url=settings.openai_base_url)
        self.model = OpenAIModel(settings.openai_model, openai_client=self.client)
        self.agent = Agent(self.model, result_type=LabelResult)
        self.results_file = settings.results_dir / "tag_classifications.json"
        
    async def process_tag(
        self, 
        tag_name: str, 
        results: ClassificationResults, 
        semaphore: asyncio.Semaphore
    ) -> Tuple[str, Optional[LabelResult]]:
        """处理单个标签"""
        async with semaphore:
            try:
                print(f"正在处理标签: {tag_name}")
                result = await self.agent.run(tag_name)
                results.add_result(tag_name, result.data)
                print(f"标签 {tag_name} 处理完成: {result.data.category} - {result.data.translation}")
                return tag_name, result.data
            except Exception as e:
                print(f"处理标签 {tag_name} 时出错: {e}")
                return tag_name, None
    
    async def process_all_tags(self) -> None:
        """处理所有标签"""
        # 加载已有结果
        results = ClassificationResults.load(self.results_file)
        
        # 加载所有标签
        all_tags = load_tags(settings.tags_file)
        print(f"从CSV加载了 {len(all_tags)} 个标签")
        print(f"已有 {len(results.results)} 个标签处理结果")
        
        # 找出未处理的标签
        tags_to_process = [tag for tag in all_tags if tag not in results.results]
        print(f"需要处理 {len(tags_to_process)} 个标签")
        
        if not tags_to_process:
            print("没有需要处理的标签，程序退出")
            return
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(settings.max_concurrency)
        
        # 创建任务
        tasks = []
        for tag in tags_to_process:
            tasks.append(self.process_tag(tag, results, semaphore))
        
        # 执行任务并显示进度
        total = len(tasks)
        completed = 0
        save_counter = 0
        start_time = time.time()
        
        for future in asyncio.as_completed(tasks):
            tag_name, result = await future
            completed += 1
            save_counter += 1
            
            # 定期保存结果
            if save_counter >= settings.save_interval:
                print(f"已处理 {completed} 个标签，保存结果...")
                results.save(self.results_file)
                save_counter = 0
            
            # 显示进度
            print(format_progress(completed, total, time.time() - start_time))
        
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
        
        # 最后保存一次
        results.save(self.results_file)
        print("所有结果已保存") 