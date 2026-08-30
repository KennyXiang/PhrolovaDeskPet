# 弗洛洛桌宠（Phrolova Desktop Pet）

一个基于 PyQt5 的简易ai桌宠程序，角色来自《鸣潮》中弗洛洛（Phrolova）的同人二创糯糯。  
支持三种移动模式、AI 对话、文件拖拽回收等功能。
<img width="266" height="221" alt="Screenshot 2026-08-30 at 11 30 03 PM" src="https://github.com/user-attachments/assets/ffd4db47-218b-4473-be6d-488b6e802960" />

---

## ✨ 功能特性

- 🖱️ **三种移动模式**：跟随鼠标、静止拖拽、自由漫游
- 💬 **AI 对话**：接入 DeepSeek 或其他 OpenAI 兼容 API
- 🗑️ **拖拽删除**：将文件拖到桌宠身上，会自动移入回收站并给出角色回复
- 🎨 **动画效果**：行走、静止的小动作
- ⌨️ **快捷键**：按 `Esc` 可快速关闭输入框或对话气泡

---

## 📦 安装与运行

### 1. 环境要求

- Python 3.8 或更高版本
- macOS / Windows / Linux（推荐 macOS，已测试打包 .app）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 AI（可选）

- 在 `ai_config.example.json` 中填写你的 `api_key` 和 `base_url`（默认使用 DeepSeek API），只兼容 OpenAI 接口协议

```json
{
    "api_key": "sk-你的真实密钥",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-v4-flash"
}
```

- **注意**：如果不配置，AI 对话功能会提示“未配置”，但其他功能（移动、拖拽）依然可用。

### 4. 运行

```bash
python Deskpet.py
```

---

## 🗂️ 项目结构

```
├── Deskpet.py          # 主程序
├── images/                   # 图片资源
│   ├── fll_still.png
│   ├── fll_run_1.png
│   └── fll_run_2.png
├── ai_config.example.json    # AI 配置模板
├── requirements.txt          # 依赖列表
└── README.md                # 本文件
```

---

## 🤝 贡献

欢迎提交 Issue 或 Pull Request。 

---

## 📄 许可证

本项目仅供学习交流使用，请勿用于商业用途。  
