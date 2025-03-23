from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    """应用配置"""
    # OpenAI配置
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_base_url: str
    
    # 文件路径配置
    base_dir: Path = Path(__file__).parent.parent.parent
    results_dir: Path = base_dir / "results"
    tags_file: Path = base_dir / "selected_tags.csv"
    
    # 处理配置
    max_concurrency: int = 100
    save_interval: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局配置实例
settings = Settings()

# 确保必要的目录存在
settings.results_dir.mkdir(exist_ok=True) 