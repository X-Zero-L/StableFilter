import asyncio
import time
import sys
from pathlib import Path

from src.core.tag_processor import TagProcessor
from src.config.settings import settings

async def main():
    """主程序入口"""
    processor = TagProcessor()
    
    try:
        await processor.process_all_tags()
    except KeyboardInterrupt:
        print("\n程序已中断")
        # 尝试保存当前结果
        try:
            results_file = settings.results_dir / "tag_classifications.json"
            if results_file.exists():
                from src.models.tag_models import ClassificationResults
                results = ClassificationResults.load(results_file)
                results.save(f"{results_file}.interrupted.{int(time.time())}")
                print("已在中断时保存当前结果")
        except Exception as e:
            print(f"中断时保存结果出错: {e}")
    except Exception as e:
        print(f"程序出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 