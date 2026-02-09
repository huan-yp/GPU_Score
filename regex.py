import re
import json
import os

print("开始处理...")
with open("raw.txt", "r", encoding="utf-8") as file:
    html_content = file.read()

# 正则匹配逻辑：匹配名称和分数
pattern = r'class="name">\s*(.*?)\s*<div.*?class="score">\s*(\d+)'
# 如果你的 HTML 结构和示例完全一致，用这个简化版：
pattern = r'class="name">\s*(.*?)\s*</td>.*?class="score">\s*(\d+)'

matches = re.findall(pattern, html_content, re.S)

# 过滤主流游戏显卡关键词（含核显）
gaming_keywords = [
    "GeForce",
    "Radeon RX",
    "Radeon Graphics",
    "Radeon Vega",
    "Radeon",
    "Intel",
    "Iris",
    "UHD",
    "HD Graphics"
]
# 数据清洗：标准化名称并去重
data_map = {}
for m in matches:
    raw_name = m[0].split('<')[0].strip()
    score = int(m[1])
    
    # 关键词过滤
    if not any(kw in raw_name for kw in gaming_keywords):
        continue

    # 过滤 NVK 开源驱动
    if "NVK" in raw_name:
        continue

    # 过滤脏数据：RadeonT 视为异常条目
    if "RadeonT" in raw_name:
        continue

    # 过滤工作站显卡、专业卡、数据中心卡
    workstation_keywords = [
        "Radeon PRO",
        "Radeon Pro",
        " PRO W",
        " WX ",
        "WX 9",
        "WX 8",
        "WX 7",
        "WX 5",
        "WX 4",
        "WX 3",
        "WX 2",
        "Radeon Vega Frontier",
        "Frontier Edition",
        "Instinct",
        "Intel Arc Pro",
        "Data Center",
        "Virtio-GPU",
        "Microsoft Direct3D12",
        "Pro Vega",
        "Pro 5700",
        "Pro 5600",
        "Pro 5500",
        "Pro 5300",
        "Pro 4",
        "W6900X",
        "W6800X",
        "W5700X",
        "Pro VII"
    ]
    if any(keyword in raw_name for keyword in workstation_keywords):
        continue

    # 过滤废数据：无具体型号的通用名称
    invalid_names = [
        "Microsoft Direct3D",
        "Intel Graphics i gfx",
        "driver-ci",
    ]
    if any(keyword in raw_name for keyword in invalid_names):
        continue
    
    # 过滤过于笼统的名称（无具体型号）
    if raw_name in ["Intel Graphics", "Radeon Graphics", "Radeon TM Graphics", "AMD Radeon Graphics"]:
        continue
    
    # 过滤单数字命名（数据错误）
    if re.match(r"^(AMD\s+)?Radeon\s+\d{1}$", raw_name, re.IGNORECASE):
        continue
    
    # 过滤TITAN系列和Radeon VII（可选：发烧级非主流卡）
    if re.search(r"\bTITAN\b", raw_name, re.IGNORECASE):
        continue
    if "Radeon VII" in raw_name:
        continue

    # 只展示官方驱动：跳过带括号的开源/平台标记条目，但保留 (TM)
    driver_markers = [
        "RADV",
        "NAVI",
        "GFX",
        "MESA",
        "AMDVLK",
        "VULKAN",
        "DIRECT3D",
        "OPENGL"
    ]
    parenthetical_parts = re.findall(r"\((.*?)\)", raw_name)
    if any(any(marker in part.upper() for marker in driver_markers) for part in parenthetical_parts):
        continue

    if score < 10 ** 4:
        continue
        
    # 标准化名称：去除厂商前缀与括号内容 (含 TM)
    clean_name = re.sub(r"\s*\(.*?\)\s*", " ", raw_name)
    clean_name = re.sub(r"\s+", " ", clean_name).strip()
    
    # 统一空格格式：修复 RX6500 -> RX 6500
    clean_name = re.sub(r"(RX)(\d)", r"\1 \2", clean_name)
    clean_name = re.sub(r"(GTX)(\d)", r"\1 \2", clean_name)
    clean_name = re.sub(r"(RTX)(\d)", r"\1 \2", clean_name)
    clean_name = re.sub(r"\s+", " ", clean_name).strip()
    
    for prefix in ["NVIDIA ", "AMD ", "ATI "]:
         if clean_name.upper().startswith(prefix): # 忽略大小写前缀检查
             clean_name = clean_name[len(prefix):]
    
    # 去重逻辑：保留最高分
    if clean_name in data_map:
        if score > data_map[clean_name]:
            data_map[clean_name] = score
    else:
        data_map[clean_name] = score

filtered_data = [{"name": name, "score": score} for name, score in data_map.items()]

# 按分数降序排列
filtered_data.sort(key=lambda x: x['score'], reverse=True)

print(f"提取并清洗数据完成，共 {len(filtered_data)} 条")

with open("filtered_data.json", "w", encoding="utf-8") as json_file:
    json.dump(filtered_data, json_file, ensure_ascii=False, indent=4)
print("已保存 filtered_data.json")

# 5. 更新 HTML (从 template.html 生成 index.html)
template_path = "template.html"
output_path = "index.html"

if os.path.exists(template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        html_source = f.read()

    # 准备 JS 数据字符串
    json_str = json.dumps(filtered_data, ensure_ascii=False, indent=4)
    
    # 构造替换内容，加上 const 声明，确保完全覆盖
    new_js_assignment = f"const gpuData = {json_str};"

    # 正则替换 HTML 中的 JS 数据部分
    # 匹配目标：const gpuData = [ ... ];
    # 兼容换行和中间的内容
    regex_pattern = r'const\s+gpuData\s*=\s*\[.*?\];'
    
    # 检查是否匹配
    if re.search(regex_pattern, html_source, re.DOTALL):
        new_html = re.sub(regex_pattern, new_js_assignment, html_source, flags=re.DOTALL)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"成功！已从 {template_path} 生成 {output_path}")
    else:
        print(f"错误：在 {template_path} 中找不到 'const gpuData = [...]' 占位符")
else:
    print(f"错误：找不到 {template_path} 模板文件")