import cv2
import numpy as np
import ezdxf
import os
import sys
from PIL import Image


def vectorize_floor_plan_v5(image_path, output_path, scale=1.0):
    pil_img = Image.open(image_path).convert("RGB")
    img = np.array(pil_img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Slightly lower threshold to catch thin partitions
    _, binary = cv2.threshold(gray, 185, 255, cv2.THRESH_BINARY_INV)

    # Crop away title block / heavy margins
    x1 = int(w * 0.16)
    y1 = int(h * 0.09)
    x2 = int(w * 0.96)
    y2 = int(h * 0.92)
    crop_bin = binary[y1:y2, x1:x2]

    # Clean small noise but preserve thin lines
    kernel = np.ones((2, 2), np.uint8)
    crop_bin = cv2.morphologyEx(crop_bin, cv2.MORPH_OPEN, kernel, iterations=1)
    crop_bin = cv2.morphologyEx(crop_bin, cv2.MORPH_CLOSE, kernel, iterations=1)

    edges = cv2.Canny(crop_bin, 50, 150)

    doc = ezdxf.new("R2010", units=ezdxf.units.MM)
    msp = doc.modelspace()
    doc.layers.add("WALLS", color=7)
    doc.layers.add("CONTOURS", color=3)
    doc.layers.add("TEXT", color=6)

    # More sensitive line detection
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=35,
        minLineLength=25,
        maxLineGap=18,
    )

    line_count = 0
    if lines is not None:
        for line in lines:
            coords = line.flatten() if hasattr(line, "flatten") else np.array(line).flatten()
            px1, py1, px2, py2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
            gx1 = x1 + px1
            gy1 = y1 + py1
            gx2 = x1 + px2
            gy2 = y1 + py2
            msp.add_line(
                (gx1 * scale, (h - gy1) * scale),
                (gx2 * scale, (h - gy2) * scale),
                dxfattribs={"layer": "WALLS"},
            )
            line_count += 1

    # All contours including interior partitions
    contours, hierarchy = cv2.findContours(crop_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_count = 0
    if contours is not None:
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 120:
                continue
            epsilon = 0.004 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            points = []
            for pt in approx:
                px, py = int(pt[0][0]), int(pt[0][1])
                gx = x1 + px
                gy = y1 + py
                points.append((gx * scale, (h - gy) * scale))
            if len(points) >= 3:
                msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "CONTOURS"})
                contour_count += 1

    msp.add_text(
        "Converted from image - verify scale before dimensioning",
        height=80,
        dxfattribs={"layer": "TEXT", "insert": (x1 * scale, (h - y2 - 100) * scale)},
    )

    doc.saveas(output_path)
    print(f"DXF saved: {output_path}")
    print(f"Lines: {line_count}, Contours: {contour_count}")

    preview = img.copy()
    if lines is not None:
        for line in lines:
            coords = line.flatten() if hasattr(line, "flatten") else np.array(line).flatten()
            px1, py1, px2, py2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
            cv2.line(preview, (x1 + px1, y1 + py1), (x1 + px2, y1 + py2), (0, 0, 255), 2)
    preview_path = os.path.splitext(output_path)[0] + "_preview.jpg"
    cv2.imwrite(preview_path, preview)
    print(f"Preview saved: {preview_path}")
    return output_path


if __name__ == "__main__":
    image_path = r"C:\Users\Administrator\Desktop\微信图片_20260908204429_419_118.jpg"
    output_path = r"C:\Users\Administrator\Desktop\floorplan_converted.dxf"
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    vectorize_floor_plan_v5(image_path, output_path)
