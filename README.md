# TextureAlphaMerger

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

一款轻量级的贴图处理工具，用于批量修改图片尺寸和合并Alpha通道。

## ✨ 功能特性

- **双模式切换** — 支持 Alpha 合成模式 与 RGB 合成模式 一键切换
- **Alpha通道合并** — 将灰度Alpha贴图自动合并到彩色图的Alpha通道
- **RGB贴图合成** — 将 R、G、B 三张通道贴图合成为一张 RGBA 图片
- **批量尺寸调整** — 支持批量调整图片尺寸（256/512/1024/2048/4096）
- **多格式支持** — 支持PNG、TGA、BMP、JPG格式导出
- **自动识别** — 根据命名后缀自动匹配贴图（Alpha模式：`_A` / `_Opacity`）
- **智能命名** — RGB 模式根据通道类型自动生成后缀（如 `_RAH`）
- **拖拽支持** — 直接拖拽文件到窗口快速添加
- **现代化UI** — 基于PySide6的白色扁平主题界面

## 📖 软件说明

### 功能简介

本软件旨在方便批量修改贴图尺寸和给图片添加Alpha通道贴图，同时支持将多张通道贴图合成为一张 RGBA 图片，适用于游戏开发、纹理处理等场景。更多功能将在后续版本中持续添加。

### 模式说明

| 模式 | 功能 | 适用场景 |
|------|------|----------|
| Alpha 合成 | 将灰度 Alpha 图合并到彩色图的 Alpha 通道 | 贴图透明度处理 |
| RGB 合成 | 将 R、G、B 三张通道图合成为一张 RGBA 图 | PBR 贴图打包（Roughness/AO/Height 等） |

### 使用说明

#### Alpha 合成模式

1. **添加彩色图**：拖拽文件到左侧彩色图区域，或点击"添加"按钮
2. **自动匹配Alpha**：软件会自动识别同目录下的 `_A` 或 `_Opacity` 后缀图片
3. **选择导出设置**：设置保存格式、尺寸和输出目录
4. **导出合成**：点击"导出合成"按钮完成处理

#### RGB 合成模式

1. **切换模式**：左上角下拉框选择"RGB 合成"
2. **选择通道类型**：分别为 R、G、B 通道选择贴图类型
3. **添加贴图**：拖拽文件到对应通道框，软件会自动匹配同目录下的相关贴图
4. **导出合成**：点击"导出合成"按钮，输出文件自动按通道类型命名

### Alpha贴图命名规则

Alpha贴图需与彩色图放在同一目录，并按以下规则命名：

| 彩色图 | Alpha图（任选其一） |
|--------|---------------------|
| `texture.png` | `texture_A.png` |
| `texture.png` | `texture_Opacity.png` |

> ⚠️ **注意**：为确保最佳效果，Alpha贴图与彩色图的分辨率应保持一致。

### RGB 通道匹配规则

RGB 合成模式下，软件支持以下通道类型的自动匹配：

| 通道类型 | 匹配后缀 |
|----------|----------|
| Roughness | `_R`, `_r`, `_Roughness`, `_roughness` |
| AO | `_AO`, `_ao`, `_AmbientOcclusion`, `_ambientocclusion` |
| Height | `_H`, `_h`, `_Height`, `_height`, `_Displacement`, `_Disp` |
| Metallic | `_M`, `_m`, `_Metallic`, `_metallic`, `_Metalness` |
| Curvature | `_Curvature`, `_curvature`, `_Curve`, `_Curv` |
| Thickness | `_Thickness`, `_thickness`, `_Thick` |

### 导出文件命名规则

#### Alpha 合成模式

| 处理类型 | 输出文件名 | 说明 |
|----------|-----------|------|
| Alpha合并 | `原名_DA.ext` | Dual Alpha，已合并Alpha通道 |
| 尺寸缩放 | `原名_1024.ext` | 无Alpha图时按指定尺寸缩放 |

#### RGB 合成模式

输出文件根据选择的通道类型自动生成后缀：

| 通道选择 | 输出后缀 | 示例 |
|----------|----------|------|
| R: Roughness, G: AO, B: Height | `_RAH` | `texture_RAH.png` |
| R: Metallic, G: Roughness, B: AO | `_MRA` | `texture_MRA.png` |
| R: AO, G: Roughness, B: Metallic | `_ARM` | `texture_ARM.png` |

## 🚀 快速开始

### 下载安装

前往 [Releases](./releases) 页面下载最新版本的可执行文件，无需安装即可运行。

### 从源码运行

**环境要求**
- Python 3.12+
- PySide6
- Pillow

**安装依赖**
```bash
pip install -r requirements.txt
```

**运行程序**
```bash
python main.py
```

## 📋 版本管理规则

本项目遵循语义化版本规范：

| 版本变更 | 类型 | 示例 | 说明 |
|----------|------|------|------|
| 主版本号 | 重大功能更新 | v1.0.0 → v2.0.0 | 架构重构、重大功能新增 |
| 次版本号 | 功能迭代优化 | v1.0.0 → v1.1.0 | 新增功能、功能优化 |
| 修订号 | Bug修复维护 | v1.0.0 → v1.0.1 | Bug修复、文档更新 |

## 📁 项目结构

```
TextureAlphaMerger/
├── main.py              # 入口文件
├── requirements.txt     # 依赖清单
├── build.spec          # PyInstaller打包配置
├── README.md           # 项目说明
├── CHANGELOG.md        # 开发日志
├── LICENSE             # 许可协议
├── releases/           # 发布版本目录
│   └── v2.0.0/
│       └── TextureAlphaMerger.exe
├── ui/
│   ├── __init__.py
│   └── main_window.py  # UI模块
├── core/
│   ├── __init__.py
│   ├── processor.py    # 图片处理核心
│   ├── updater.py      # 自动更新模块
│   └── version.py      # 版本管理
└── utils/
    ├── __init__.py
    └── file_utils.py   # 工具函数
```

## 🤝 参与贡献

欢迎参与本项目的开发与维护！

### 如何贡献

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 贡献指南

- 代码风格请遵循 PEP 8 规范
- 提交前请确保代码可正常运行
- 新功能请添加相应的文档说明

## 📄 许可协议

本项目采用 **GNU General Public License v3.0** 协议开源。

### 您可以

- ✅ 自由使用、复制、分发本软件
- ✅ 修改本软件或基于本软件进行创作
- ✅ 将修改后的软件分发给他⼈

### 协议要求

- 📝 **保留版权声明** — 必须保留原作者的版权声明和许可声明
- 🔓 **相同协议开源** — 任何基于本软件的衍生作品必须以 GPL v3.0 协议开源
- 📄 **提供源代码** — 分发时必须提供源代码或获取源代码的方式

### ⚠️ 特别说明

> 本项目初衷是供学习和个人使用。如果您希望将本软件用于商业目的，请先与作者取得联系并获得书面授权。

完整协议内容请参阅 [LICENSE](./LICENSE) 文件或访问 [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0/)。

## 📮 联系方式

如有问题或建议，欢迎提交 [Issue](../../issues)。

---

*Made with ❤️ by TextureAlphaMerger Team*
