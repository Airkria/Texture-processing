# -*- coding: utf-8 -*-
"""图片处理核心模块"""

import os
from PIL import Image


class ImageProcessor:
    """图片处理器"""

    SUPPORTED_FORMATS = {'.png', '.tga', '.bmp', '.jpg', '.jpeg'}

    def __init__(self):
        self.processed_count = 0
        self.resized_count = 0  # 【逻辑2】新增：缩放处理计数
        self.failed_files = []
        self.skipped_files = []

    def merge_alpha(self, color_image_path: str, alpha_image_path: str,
                    output_path: str, output_format: str = 'PNG',
                    output_size: int = None) -> bool:
        """
        将Alpha图合并到彩色图的Alpha通道

        Args:
            color_image_path: 彩色图路径
            alpha_image_path: Alpha图路径
            output_path: 输出文件路径
            output_format: 输出格式 (PNG, TGA, BMP, JPG)
            output_size: 输出尺寸（可选，如1024表示1024x1024）

        Returns:
            bool: 是否成功
        """
        try:
            # 打开彩色图
            color_img = Image.open(color_image_path).convert('RGBA')

            # 打开Alpha图并转换为灰度
            alpha_img = Image.open(alpha_image_path).convert('L')

            # 确保尺寸匹配
            if color_img.size != alpha_img.size:
                alpha_img = alpha_img.resize(color_img.size, Image.LANCZOS)

            # 将Alpha图的灰度值作为Alpha通道
            color_img.putalpha(alpha_img)

            # 如果指定了输出尺寸，进行缩放
            if output_size:
                color_img = color_img.resize((output_size, output_size), Image.LANCZOS)

            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 根据格式保存
            self._save_image(color_img, output_path, output_format)

            self.processed_count += 1
            return True

        except Exception as e:
            self.failed_files.append((color_image_path, str(e)))
            return False

    def resize_image(self, color_image_path: str, output_path: str,
                     output_format: str = 'PNG', output_size: int = None) -> bool:
        """
        【逻辑2】缩放图片（无Alpha图时使用）

        Args:
            color_image_path: 彩色图路径
            output_path: 输出文件路径
            output_format: 输出格式 (PNG, TGA, BMP, JPG)
            output_size: 输出尺寸

        Returns:
            bool: 是否成功
        """
        try:
            # 打开彩色图
            color_img = Image.open(color_image_path)

            # 转换为RGBA（如果是JPG输出且没有Alpha通道，后续会转换）
            if color_img.mode != 'RGBA':
                color_img = color_img.convert('RGBA')

            # 缩放
            if output_size:
                color_img = color_img.resize((output_size, output_size), Image.LANCZOS)

            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 根据格式保存
            self._save_image(color_img, output_path, output_format)

            self.resized_count += 1
            return True

        except Exception as e:
            self.failed_files.append((color_image_path, str(e)))
            return False

    def _save_image(self, img: Image.Image, output_path: str, output_format: str):
        """
        根据格式保存图片

        Args:
            img: PIL图像对象
            output_path: 输出路径
            output_format: 输出格式
        """
        output_format = output_format.upper()

        if output_format == 'TGA':
            img.save(output_path, 'TGA')
        elif output_format == 'JPG' or output_format == 'JPEG':
            # JPG不支持Alpha通道，需要转换为RGB
            if img.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 使用Alpha通道作为mask
                background.save(output_path, 'JPEG', quality=95)
            else:
                img.save(output_path, 'JPEG', quality=95)
        else:
            # PNG, BMP等
            img.save(output_path, output_format)

    def merge_files_with_mapping(self, color_files: list, alpha_files: list,
                                  output_dir: str = None,
                                  output_format: str = 'PNG',
                                  output_size: int = None,
                                  progress_callback=None) -> dict:
        """
        合并文件列表中的图片（彩色图与Alpha图一一对应）

        【逻辑2】新增：如果没有Alpha图，检测原尺寸和保存尺寸是否相同，
        若不相同则按保存尺寸进行保存并添加后缀

        Args:
            color_files: 彩色图文件路径列表
            alpha_files: Alpha图文件路径列表（与color_files一一对应，None表示无匹配）
            output_dir: 输出目录（如果为空则使用各彩色图的源目录）
            output_format: 输出格式
            output_size: 输出尺寸（可选）
            progress_callback: 进度回调函数 callback(current, total, filename)

        Returns:
            dict: 处理结果
        """
        self.processed_count = 0
        self.resized_count = 0
        self.failed_files = []
        self.skipped_files = []

        total = len(color_files)

        for idx, (color_file, alpha_file) in enumerate(zip(color_files, alpha_files), 1):
            filename = os.path.basename(color_file)
            name_no_ext = os.path.splitext(filename)[0]

            # 确定输出目录
            if output_dir:
                target_dir = output_dir
            else:
                target_dir = os.path.dirname(color_file)

            if alpha_file is not None:
                # 情况1：有对应的Alpha图，合并到Alpha通道
                ext = self._get_extension(output_format)
                output_filename = name_no_ext + '_DA' + ext
                output_path = os.path.join(target_dir, output_filename)

                self.merge_alpha(color_file, alpha_file, output_path, output_format, output_size)

            elif output_size is not None:
                # 【逻辑2】情况2：无Alpha图，检查是否需要缩放
                try:
                    with Image.open(color_file) as img:
                        original_size = img.size[0]  # 获取宽度（假设正方形或取宽度）

                    if original_size != output_size:
                        # 原尺寸与目标尺寸不同，进行缩放
                        ext = self._get_extension(output_format)
                        output_filename = f"{name_no_ext}_{output_size}{ext}"
                        output_path = os.path.join(target_dir, output_filename)

                        self.resize_image(color_file, output_path, output_format, output_size)
                    else:
                        # 原尺寸与目标尺寸相同，跳过
                        self.skipped_files.append(color_file)

                except Exception as e:
                    self.failed_files.append((color_file, str(e)))
            else:
                # 无Alpha图且未指定输出尺寸，跳过
                self.skipped_files.append(color_file)

            # 进度回调
            if progress_callback:
                progress_callback(idx, total, filename)

        return {
            'success': self.processed_count,
            'resized': self.resized_count,  # 【逻辑2】新增缩放计数
            'failed': len(self.failed_files),
            'skipped': len(self.skipped_files),
            'failed_files': self.failed_files,
            'skipped_files': self.skipped_files
        }

    def _get_extension(self, output_format: str) -> str:
        """获取输出文件扩展名"""
        format_map = {
            'PNG': '.png',
            'TGA': '.tga',
            'BMP': '.bmp',
            'JPG': '.jpg',
            'JPEG': '.jpg'
        }
        return format_map.get(output_format.upper(), '.png')
