# floorplan-to-dxf

> 把户型平面图（照片 / 扫描件 / CAD 截图）自动转成可编辑的 **DXF CAD 图纸**——为后续的 3D 建模、AI 渲染工作流提供矢量化起点。

[![Type](https://img.shields.io/badge/type-AI--Skill-A8502A)]() [![Stack](https://img.shields.io/badge/OpenCV%20%2B%20ezdxf-Python-2F5D62)]() [![Output](https://img.shields.io/badge/输出-DXF%20%2B%20预览图-4A4640)]()

---

## 解决什么问题

做户型改造、效果图、3D 建模时，第一步往往卡在同一个地方：**手上只有一张平面图的 JPG，没有 CAD 源文件**。

手动描图一张 200㎡ 的户型，认真描要 1–2 小时，还不一定准。这个脚本把这步自动化：输入图片，输出带图层的 DXF，可以直接在 CAD 里继续编辑。

## 核心用法

```bash
python scripts/image_to_dxf_v5.py <input.jpg> [output.dxf]
```

默认输出到桌面，同时生成一张预览 JPG（方便核对转换质量）。

**批量转换：**

```bash
python scripts/image_to_dxf_v5.py --batch <input_dir> --output <output_dir>
```

## 处理流程

1. Pillow 读图（兼容中文路径）
2. OpenCV 灰度 + 二值化，自动裁剪掉左侧图签和页边
3. Canny 边缘检测 + HoughLinesP 直线提取墙体/分隔线
4. 轮廓近似生成闭合多段线
5. ezdxf 写入 DXF，按语义分图层

## 图层输出

| DXF 图层 | 内容 | CAD 颜色 |
|-----------|------|-----------|
| WALLS | 墙体 / 承重墙线 | 白 (7) |
| CONTOURS | 轮廓 / 非承重分隔 | 黄 (2) |
| TEXT | 文字标注 | 绿 (3) |
| DOORS | 门洞标记 | 红 (1) |
| WINDOWS | 窗户标记 | 青 (4) |

分图层的好处：导入 CAD 后可以单独开关、单独改色、单独提取墙体做后续建模，不用从一张"糊在一起"的线图里手工挑。

## 参数调优

| 参数 | 默认值 | 什么时候要调 |
|------|--------|--------------|
| `threshold` | 185 | 图偏淡 → 降到 170–180 |
| `minLineLength` | 25 | 需要捕捉更细的线 → 降到 15（代价：会引入噪点） |
| `maxLineGap` | 18 | 墙体是双线且断得多 → 适当增大 |
| 裁剪范围 | x: 0.16–0.96, y: 0.09–0.92 | 图签位置不同时调整 |

## 与下游工作流衔接

DXF 输出后可以直接接：

1. **AI 效果图提示词** — 从 DXF 提取空间布局生成渲染 prompt
2. **ComfyUI + ControlNet** — DXF 作为深度图 / 线稿控制
3. **Blender Python API** — 导入 DXF 建 3D 模型

## 使用限制（重要）

- 输入图分辨率 < 1000px 宽度时效果明显下降，建议先放大
- 手绘户型图效果不如 CAD 截图（线条粗细不均）
- 彩色平面图需先做色彩分离，否则噪点多
- 厚墙会产生双线，导出后建议在 CAD 里手工清理一次
- 输出 DXF 单位为 mm，Y 轴已翻转为 CAD 常规朝向；**比例需在 CAD 中按图纸标注尺寸缩放校准**

## 依赖

```
opencv-python ezdxf numpy scikit-image pillow
```

---

## License

MIT
