from typing import Literal, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class LabelResult(BaseModel):
    """标签分类结果模型"""
    category: Literal["general", "sensitive", "nsfw", "explicit"] = Field(
        ..., description="分类标签, 可选值: general, sensitive, nsfw, explicit"
    )
    explanation: str = Field(..., description="对分类结果的详细中文解释说明")
    translation: str = Field(..., description="标签的中文翻译")

class TagClassification(BaseModel):
    """单个标签的分类结果"""
    tag: str
    result: LabelResult
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ClassificationResults(BaseModel):
    """所有标签的分类结果集合"""
    results: Dict[str, TagClassification] = {}
    
    def add_result(self, tag: str, result: LabelResult) -> None:
        """添加一个新的分类结果"""
        self.results[tag] = TagClassification(tag=tag, result=result)
    
    def save(self, filename: str) -> None:
        """保存结果到文件"""
        import json
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, filename: str) -> "ClassificationResults":
        """从文件加载结果"""
        import json
        import os
        
        if not os.path.exists(filename):
            return cls()
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls.parse_obj(data)
        except Exception as e:
            print(f"加载文件 {filename} 时出错: {e}")
            return cls() 