import csv
import re
import json
import os
from collections import OrderedDict

MODULE_DIR = os.path.dirname(os.path.dirname(__file__))

def load_rules(rules_file=os.path.join(MODULE_DIR, 'actions', 'classification_rules.json')):
    """从JSON文件加载分类规则"""
    with open(rules_file, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    # 转换为OrderedDict保持顺序
    return OrderedDict(rules)

def classify_action(action: str, rules: OrderedDict) -> str:
    """使用规则分类动作"""
    # print(f"分类动作: {action}")
    action_lower = action.lower()
    for label, patterns in rules.items():
        for pattern in patterns:
            # print(f"匹配模式: {pattern}")
            if re.search(pattern.lower(), action_lower):
                return label
    return "未分类"


def classify_csv(input_file=os.path.join(MODULE_DIR, 'actions', 'actions.csv'),
                output_file=os.path.join(MODULE_DIR, 'actions', 'classified_actions.csv'),
                rules_file=os.path.join(MODULE_DIR, 'actions', 'classification_rules.json')):
    """分类CSV文件中的动作"""
    rules = load_rules(rules_file)
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # 写入表头
        writer.writerow(['timestamp', 'original_action', 'classified_action'])
        
        next(reader)  # 跳过原始表头
        for row in reader:
            if len(row) < 2:  # 跳过不完整的行
                continue
            timestamp, action = row[:2]
            classification = classify_action(action, rules)
            writer.writerow([timestamp, action, classification])
    
    print(f"分类完成，输出文件为 {output_file}")

if __name__ == "__main__":
    # 示例：可以自定义文件路径
    classify_csv(
        input_file=os.path.join(MODULE_DIR, 'actions', 'actions.csv'),
        output_file=os.path.join(MODULE_DIR, 'actions', 'classified_actions.csv'),
        rules_file=os.path.join(MODULE_DIR, 'actions', 'classification_rules.json')
    )
