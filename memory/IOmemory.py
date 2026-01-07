import csv
import os
from creat import creatmemory
from datetime import datetime

creatmemory()

MODULE_DIR = os.path.dirname(os.path.dirname(__file__))

# 常量定义
MEMORY_FILE = os.path.join(MODULE_DIR, 'memory', 'memory.csv')
ALIAS_FILE = os.path.join(MODULE_DIR, 'memory', 'alias_mapping.csv')

# 加载别名映射表
def load_alias_mapping():
    mapping = {}
    if os.path.exists(ALIAS_FILE):
        with open(ALIAS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mapping[row['alias']] = row['main_key']
    return mapping

# 保存别名映射表
def save_alias_mapping(mapping):
    with open(ALIAS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['alias', 'main_key'])
        writer.writeheader()
        for alias, main_key in mapping.items():
            writer.writerow({'alias': alias, 'main_key': main_key})

# 获取主键（带别名处理）
def get_main_key(key, mapping):
    if isinstance(key, list):
        for k in key:
            if k in mapping:
                return mapping[k]
        return key[0]  # 默认取第一个作为主键
    return mapping.get(key, key)

# 写入记忆（支持多近义词）
def write_memory(time, keys, content):
    # 处理时间
    if not time:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 处理别名
    alias_mapping = load_alias_mapping()
    main_key = get_main_key(keys, alias_mapping)
    
    # 更新别名映射表
    if isinstance(keys, list):
        for key in keys:
            if key != main_key and key not in alias_mapping:
                alias_mapping[key] = main_key
        save_alias_mapping(alias_mapping)
    
    # 读取现有数据
    headers = ['time']
    rows = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, ['time'])
            rows = list(reader)
    
    # 添加新列
    if main_key not in headers:
        headers.append(main_key)
        for row in rows:
            row += [''] * (len(headers) - len(row))
    
    # 查找或创建行
    found = False
    for i, row in enumerate(rows):
        if row and row[0] == time:
            # 扩展行长度
            row += [''] * (len(headers) - len(row))
            row[headers.index(main_key)] = content
            found = True
            break
    
    if not found:
        new_row = [time] + [''] * (len(headers) - 1)
        new_row[headers.index(main_key)] = content
        rows.append(new_row)
    
    # 写入文件
    with open(MEMORY_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def read_memory(time=None, key=None, content_key=None):
    results = []
    alias_mapping = load_alias_mapping()
    
    if not os.path.exists(MEMORY_FILE):
        return results
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        
        # 准备两个结果集：精确匹配结果和全部结果
        exact_matches = []
        all_contents = []
        
        for row in reader:
            # 时间匹配过滤
            if time and (time in row['time']):
                continue
            
            # 主键解析
            main_key = get_main_key(key, alias_mapping) if key else None
            
            if main_key:
                if main_key not in row:
                    continue
                
                content = row[main_key]

                if not content: 
                    continue

                entry = {
                    'time': row['time'],
                    'key': main_key,
                    'content': content
                }
                
                # 始终收集到全部结果集
                all_contents.append(entry)
                
                # 当有content_key时记录精确匹配
                if content_key:
                    if content_key in content:
                        exact_matches.append(entry)
            else:
                # 全局搜索逻辑保持不变
                for col in headers:
                    if col == 'time':
                        continue
                    content = row.get(col, '')
                    entry = {
                        'time': row['time'],
                        'key': col,
                        'content': content
                    }
                    all_contents.append(entry)
                    if content_key and content_key in content:
                        exact_matches.append(entry)

        # 结果判定逻辑
        if content_key:
            # 有精确匹配时返回精确结果，否则返回全部内容
            results = exact_matches if exact_matches else all_contents
        else:
            # 无content_key时直接返回全部内容
            results = all_contents
            
    return results

# 示例使用
if __name__ == "__main__":
    # 写入示例
    write_memory("2023-10-01", ["爱好", "喜好"], "墨白喜欢听音乐")
    write_memory("", ["事件", "活动"], "收养了一只小猫")
    
    # 读取示例
    print("全局搜索'小猫':")
    print(read_memory(content_key="小猫"))
    
    print("\n指定时间搜索:")
    print(read_memory(time="2023-10-01", key="爱好"))
    
    print("\n近义词搜索:")
    print(read_memory(key="喜好"))