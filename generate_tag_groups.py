import os
import json
from typing import Dict, List, Set
from collections import defaultdict
import csv

# 加载分类结果
def load_classification_results():
    results_file = os.path.join(os.path.dirname(__file__), "results", "tag_classifications.json")
    
    if not os.path.exists(results_file):
        print(f"错误: 找不到分类结果文件 {results_file}")
        return None
    
    try:
        with open(results_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"加载分类结果时出错: {e}")
        return None


# 按分类组织标签
def organize_tags_by_category(results):
    categories = {
        "general": set(),
        "sensitive": set(),
        "nsfw": set(),
        "explicit": set()
    }
    
    translations = {}
    
    for tag_data in results["results"].values():
        tag = tag_data["tag"]
        category = tag_data["result"]["category"]
        translation = tag_data["result"]["translation"]
        
        categories[category].add(tag)
        translations[tag] = translation
    
    return categories, translations


# 生成标签组合文件
def generate_tag_combinations(categories, translations):
    output_dir = os.path.join(os.path.dirname(__file__), "tag_groups")
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成不同级别的标签组合
    combinations = {
        "general": categories["general"],
        "general_sensitive": categories["general"].union(categories["sensitive"]),
        "general_sensitive_nsfw": categories["general"].union(categories["sensitive"]).union(categories["nsfw"]),
        "all": categories["general"].union(categories["sensitive"]).union(categories["nsfw"]).union(categories["explicit"]),
        "sensitive": categories["sensitive"],
        "nsfw": categories["nsfw"],
        "explicit": categories["explicit"],
        "sensitive_plus": categories["sensitive"].union(categories["nsfw"]).union(categories["explicit"]),
        "nsfw_plus": categories["nsfw"].union(categories["explicit"])
    }
    
    # 保存为CSV文件
    for name, tags in combinations.items():
        output_file = os.path.join(output_dir, f"{name}_tags.csv")
        
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tag", "translation"])
            
            for tag in sorted(tags):
                writer.writerow([tag, translations.get(tag, "")])
        
        print(f"已生成 {name} 标签组合，包含 {len(tags)} 个标签: {output_file}")
    
    # 生成逗号分隔的标签列表文件
    for name, tags in combinations.items():
        output_file = os.path.join(output_dir, f"{name}_tags.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(",".join(sorted(tags)))
        
        print(f"已生成 {name} 标签列表: {output_file}")
    
    # 生成带翻译的JSON文件
    for name, tags in combinations.items():
        output_file = os.path.join(output_dir, f"{name}_tags.json")
        
        tag_dict = {tag: translations.get(tag, "") for tag in sorted(tags)}
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(tag_dict, f, ensure_ascii=False, indent=2)
        
        print(f"已生成 {name} 标签JSON: {output_file}")


# 生成统计报告
def generate_statistics(categories):
    print("\n标签分类统计:")
    for category, tags in categories.items():
        print(f"  - {category}: {len(tags)} 个标签")
    
    total = sum(len(tags) for tags in categories.values())
    print(f"  - 总计: {total} 个标签")


# 主函数
def main():
    print("开始生成标签组合...")
    
    # 加载分类结果
    results = load_classification_results()
    if not results:
        return
    
    # 按分类组织标签
    categories, translations = organize_tags_by_category(results)
    
    # 生成统计报告
    generate_statistics(categories)
    
    # 生成标签组合
    generate_tag_combinations(categories, translations)
    
    print("\n标签组合生成完成!")


if __name__ == "__main__":
    main() 