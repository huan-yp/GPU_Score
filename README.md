# 主流游戏显卡性能排行榜

基于 Geekbench Vulkan 跑分数据的显卡性能对比工具。

[View it on Web](https://huan-yp.github.io/GPU_Score/)

## 数据来源

- **Geekbench Vulkan Benchmarks**: https://browser.geekbench.com/vulkan-benchmarks
- 数据通过 `regex.py` 脚本从原始 HTML 中提取、清洗并自动生成可视化页面

## 功能特性

- 📊 **动态筛选**：按评分、型号搜索、显卡系列快速筛选
- 🏷️ **系列分类**：支持 NVIDIA RTX/GTX、AMD RX、核显等系列一键选择
- 💻 **设备类型**：Mobile/Laptop 显卡默认隐藏，可选展示
- ✅ **对比模式**：支持勾选多款显卡进行性能对比
- 📈 **性能可视化**：直观的进度条展示相对性能

## 使用方法

1. 更新原始数据：将 Geekbench 页面源码保存为 `raw.txt`
2. 运行数据处理脚本：
   ```bash
   python regex.py
   ```
3. 打开 `index.html` 查看可视化结果

## 数据说明

- **已过滤项**：开源驱动标记（RADV/NVK）、工作站显卡（Pro/WX 系列）、数据中心卡、无效数据
- **评分基准**：Vulkan Compute 性能测试，分数越高性能越强
- **去重策略**：同款显卡保留最高分，自动合并命名差异

## 文件结构

- `raw.txt` - 原始 HTML 数据
- `regex.py` - 数据提取与清洗脚本
- `template.html` - 页面模板
- `index.html` - 生成的可视化页面
- `filtered_data.json` - 清洗后的 JSON 数据

## License

MIT
