#!/usr/bin/env python3
"""
在图像上绘制绿色边界框并保存 / Draw green bounding box on image and save
支持归一化 xyxy 坐标转换为像素坐标
"""

import argparse
import os
import cv2
import numpy as np


def parse_xyxy(xyxy_str):
    """解析 xyxy 字符串为归一化坐标列表"""
    try:
        coords = [float(x.strip()) for x in xyxy_str.split(',')]
        if len(coords) != 4:
            raise ValueError(f"Expected 4 values, got {len(coords)}")
        return coords  # [xmin, ymin, xmax, ymax]
    except Exception as e:
        raise ValueError(f"Invalid xyxy format: {xyxy_str}. Expected: xmin,ymin,xmax,ymax")


def xyxy_to_pixels(xyxy, img_width, img_height):
    """将归一化 xyxy 转换为像素坐标"""
    xmin, ymin, xmax, ymax = xyxy
    pxmin = int(xmin * img_width)
    pymin = int(ymin * img_height)
    pxmax = int(xmax * img_width)
    pymax = int(ymax * img_height)
    return pxmin, pymin, pxmax, pymax


def draw_bounding_box(image, xyxy, color=(0, 255, 0), thickness=3):
    """在图像上绘制边界框"""
    h, w = image.shape[:2]
    pxmin, pymin, pxmax, pymax = xyxy_to_pixels(xyxy, w, h)
    
    # 绘制矩形
    cv2.rectangle(image, (pxmin, pymin), (pxmax, pymax), color, thickness)
    
    # 可选：添加标签
    label = f"({xyxy[0]:.2f}, {xyxy[1]:.2f})"
    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(image, (pxmin, pymin - label_size[1] - 5), (pxmin + label_size[0], pymin), color, -1)
    cv2.putText(image, label, (pxmin, pymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    return image


def main(args=None):
    parser = argparse.ArgumentParser(description='Draw bounding box on image / 在图像上绘制边界框')
    parser.add_argument('--input', '-i', type=str, required=True, help='Input image path / 输入图像路径')
    parser.add_argument('--output', '-o', type=str, default=None, help='Output image path / 输出图像路径')
    parser.add_argument('--xyxy', type=str, required=True, help='Normalized xyxy coords: xmin,ymin,xmax,ymax (0-1) / 归一化坐标')
    parser.add_argument('--color', type=str, default='0,255,0', help='Box color (B,G,R), default green / 框颜色，默认绿色')
    parser.add_argument('--thickness', type=int, default=3, help='Line thickness / 线粗细')
    
    parsed_args, _ = parser.parse_known_args(args)
    
    # 解析颜色
    try:
        color = tuple(int(x.strip()) for x in parsed_args.color.split(','))
        if len(color) != 3:
            raise ValueError()
    except:
        color = (0, 255, 0)  # 默认绿色
    
    # 解析 xyxy
    xyxy = parse_xyxy(parsed_args.xyxy)
    
    # 验证 xyxy 范围
    for coord in xyxy:
        if not (0 <= coord <= 1):
            raise ValueError(f"xyxy values must be in [0, 1], got {xyxy}")
    
    # 读取图像
    if not os.path.exists(parsed_args.input):
        raise FileNotFoundError(f"Input image not found: {parsed_args.input}")
    
    image = cv2.imread(parsed_args.input)
    if image is None:
        raise ValueError(f"Failed to read image: {parsed_args.input}")
    
    # 绘制边界框
    marked_image = draw_bounding_box(image.copy(), xyxy, color, parsed_args.thickness)
    
    # 确定输出路径
    if parsed_args.output:
        output_path = parsed_args.output
    else:
        # 在文件名后添加 _marked
        base, ext = os.path.splitext(parsed_args.input)
        output_path = f"{base}_marked{ext}"
    
    # 保存图像
    if output_path.lower().endswith(('.jpg', '.jpeg')):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        cv2.imwrite(output_path, marked_image, encode_param)
    else:
        cv2.imwrite(output_path, marked_image)
    
    print(f"Marked image saved: {output_path}")
    print(f"xyxy (normalized): {xyxy}")
    
    # 返回坐标信息（供其他程序解析）
    return xyxy


if __name__ == '__main__':
    import sys
    try:
        xyxy = main()
        # 输出 JSON 格式供解析
        print(f"RESULT_JSON:{{\"xyxy\": {xyxy}}}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
