---
agent_created: true
name: floorplan-to-dxf
description: 将 JPG/PNG 户型平面图自动转换为 CAD DXF 图纸，保留墙体和主要分隔线。支持批量转换、尺寸校验、图层映射。适用于天玺湾等户型项目的2D转3D工作流。
version: 2.0
tags: [cad, dxf, floorplan, opencv, vectorization, 瓷砖, 户型]
trigger:
  - 户型转CAD
  - 平面图转DXF
  - floorplan to dxf
  - 户型图转图纸
  - CAD转换
---

# floorplan-to-dxf

把建筑/户型平面图照片或扫描件转成可编辑的 DXF CAD 文件。

## 核心用法

```bash
PYTHON_PATH=C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe
$PYTHON_PATH "SKILL_DIR/scripts/image_to_dxf_v5.py" <input.jpg> [output.dxf]
```

默认输出到桌面 `floorplan_converted.dxf`，同时生成 `floorplan_converted_preview.jpg` 预览。

## 批量转换

```bash
$PYTHON_PATH "SKILL_DIR/scripts/image_to_dxf_v5.py" --batch <input_dir> --output <output_dir>
```

批量处理目录下所有 `.jpg/.png` 文件，输出到指定目录。

## 流程

1. Pillow 读图（兼容中文路径）。
2. OpenCV 灰度 + 二值化，裁剪掉左侧图签和页边。
3. Canny 边缘 + HoughLinesP 提取墙体/分隔线。
4. 轮廓近似生成闭合多段线。
5. ezdxf 写入 DXF，图层 WALLS / CONTOURS / TEXT。

## 参数调整

| 参数 | 默认值 | 调整建议 |
|------|--------|----------|
| `threshold` | 185 | 图淡降到 170-180 |
| `minLineLength` | 25 | 降到 15 捕捉更细线，但会引入噪点 |
| `maxLineGap` | 18 | 墙体双线多可适当增大 |
| 裁剪范围 | x:0.16-0.96, y:0.09-0.92 | 按实际图签位置调整 |

## 图层映射规则

| DXF 图层 | 内容 | 颜色(CAD) |
|-----------|------|-----------|
| WALLS | 墙体/承重墙线 | 白色(7) |
| CONTOURS | 轮廓/非承重分隔 | 黄色(2) |
| TEXT | 文字标注（如有OCR） | 绿色(3) |
| DOORS | 门洞标记 | 红色(1) |
| WINDOWS | 窗户标记 | 青色(4) |

## 尺寸校验

转换后建议在 CAD 中校验：
1. 测量已知尺寸（如标注的"203㎡"对应面积）
2. 比例按像素 1:1，需在 CAD 中按图纸标注尺寸缩放
3. 厚墙产生双线，建议手动清理

## 输出规范

- DXF 单位为 mm，坐标系 Y 轴已翻转（CAD 常规向上为正）
- 文件命名：`{项目名}_{户型号}.dxf`（如 `天玺湾_9栋503.dxf`）
- 同时输出预览 JPG，用于后续 AI 渲染工作流

## 与 AI 渲染工作流衔接

DXF 输出后可直接用于：
1. **render-prompt-expert** — 从 DXF 提取空间布局生成渲染提示词
2. **ComfyUI + ControlNet** — DXF 作为深度图/线稿控制
3. **Blender Python API** — 导入 DXF 建3D模型

## 依赖

```
opencv-python ezdxf numpy scikit-image pillow
```

## 翻车规避

- 输入图分辨率 < 1000px 宽度时效果差，建议先放大
- 手绘户型图效果不如CAD截图，线条粗细不均
- 彩色平面图需先做色彩分离，否则噪点多
