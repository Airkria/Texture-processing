# -*- coding: utf-8 -*-
"""图片处理核心模块"""

import os
from PIL import Image

# 颜色图后缀（会被替换为 _DA）
COLOR_SUFFIXES = ['_D', '_Color', '_Albedo', '_BaseColor', '_Diffuse', '_Base', '_Col']
# 尺寸相关后缀（用于识别和替换）
SIZE_SUFFIXES = ['_4K', '_2K', '_1K', '_512', '_256', '_128', '_4096', '_2048', '_1024', '_0512', '_0256', '_0128']
# PBR类型后缀（尺寸后缀放在这些之前）
TYPE_SUFFIXES = [
    '_Normal', '_Norm', '_N',
    '_Roughness', '_Rough', '_R',
    '_Metallic', '_Metal', '_M',
    '_AO', '_AmbientOcclusion',
    '_Height', '_Displacement', '_Disp',
    '_Opacity', '_Alpha', '_A',
    '_Translucency', '_Tra',
    '_Emissive', '_Emission', '_E',
    '_Specular', '_Spec',
    '_Glossiness', '_Gloss',
    '_Curvature', '_Curv',
    '_ID', 
    '_Mask','_MRO','_ORM',
]


def parse_texture_name(name: str) -> dict:
    """
    解析纹理名称，提取基础名、尺寸后缀、类型后缀

    Args:
        name: 文件名（不含扩展名）

    Returns:
        dict: {
            'base': 基础名称,
            'size_suffix': 尺寸后缀或None,
            'type_suffix': 类型后缀或None,
            'is_color': 是否为颜色图
        }
    """
    base = name
    size_suffix = None
    type_suffix = None
    is_color = False

    # 检测类型后缀
    for ts in TYPE_SUFFIXES:
        if base.endswith(ts):
            type_suffix = ts
            base = base[:-len(ts)]
            break

    # 检测颜色后缀（特殊类型，会被替换为 _DA）
    for cs in COLOR_SUFFIXES:
        if base.endswith(cs):
            is_color = True
            type_suffix = cs  # 当作类型后缀处理
            base = base[:-len(cs)]
            break

    # 检测尺寸后缀
    for ss in SIZE_SUFFIXES:
        if base.endswith(ss):
            size_suffix = ss
            base = base[:-len(ss)]
            break

    return {
        'base': base,
        'size_suffix': size_suffix,
        'type_suffix': type_suffix,
        'is_color': is_color
    }


def get_output_name(color_name_no_ext: str, output_size: int = None) -> str:
    """
    根据彩色图名称生成输出文件名（有Alpha合成）

    规则：
    1. 解析基础名、尺寸、类型
    2. 颜色后缀替换为 _DA
    3. 格式：基础名_尺寸_DA

    Examples:
        T_Grass_D -> T_Grass_DA
        T_Grass_2K_D + 1024 -> T_Grass_1024_DA
        Long_Purple_Flag_2K_BaseColor + 1024 -> Long_Purple_Flag_1024_DA
    """
    parsed = parse_texture_name(color_name_no_ext)
    base = parsed['base']

    if output_size:
        return f"{base}_{output_size}_DA"
    else:
        return f"{base}_DA"


def get_resize_output_name(color_name_no_ext: str, output_size: int) -> str:
    """
    仅缩放时的输出文件名（无Alpha合成）

    规则：
    1. 解析基础名、尺寸、类型
    2. 替换/添加尺寸后缀
    3. 格式：基础名_尺寸_类型（类型保留原样）

    Examples:
        T_Grass_2K_D + 512 -> T_Grass_512_D
        Long_Purple_Flag_2K_Normal + 1024 -> Long_Purple_Flag_1024_Normal
        T_Grass_Normal + 512 -> T_Grass_512_Normal
    """
    parsed = parse_texture_name(color_name_no_ext)
    base = parsed['base']
    type_suffix = parsed['type_suffix'] or ''

    return f"{base}_{output_size}{type_suffix}"


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
                output_filename = get_output_name(name_no_ext, output_size) + ext
                output_path = os.path.join(target_dir, output_filename)

                self.merge_alpha(color_file, alpha_file, output_path, output_format, output_size)

            elif output_size is not None:
                # 【逻辑2】情况2：无Alpha图，检查是否需要缩放
                try:
                    with Image.open(color_file) as img:
                        original_size = img.size[0]  # 获取宽度（假设正方形或取宽度）

                    if original_size != output_size:
                        # 原尺寸与目标尺寸不同，进行缩放（不加_DA）
                        ext = self._get_extension(output_format)
                        output_filename = get_resize_output_name(name_no_ext, output_size) + ext
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

    def merge_rgb_channels(self, r_image_path: str, g_image_path: str, b_image_path: str,
                           output_path: str, output_format: str = 'PNG',
                           output_size: int = None) -> bool:
        """
        将R、G、B三个通道贴图合成为一张RGB图片

        Args:
            r_image_path: R通道图片路径
            g_image_path: G通道图片路径
            b_image_path: B通道图片路径
            output_path: 输出文件路径
            output_format: 输出格式 (PNG, TGA, BMP, JPG)
            output_size: 输出尺寸（可选，如1024表示1024x1024）

        Returns:
            bool: 是否成功
        """
        try:
            # 打开各通道图片并转换为灰度
            r_img = Image.open(r_image_path).convert('L') if r_image_path else None
            g_img = Image.open(g_image_path).convert('L') if g_image_path else None
            b_img = Image.open(b_image_path).convert('L') if b_image_path else None

            # 确定输出尺寸（优先使用output_size，否则使用第一个有效图片的尺寸）
            if output_size:
                target_size = (output_size, output_size)
            else:
                # 找到第一个有效的图片获取尺寸
                for img in [r_img, g_img, b_img]:
                    if img is not None:
                        target_size = img.size
                        break
                else:
                    return False  # 没有任何有效图片

            # 创建各通道图像（如果没有则使用黑色填充）
            if r_img:
                if r_img.size != target_size:
                    r_img = r_img.resize(target_size, Image.LANCZOS)
                r_channel = r_img
            else:
                r_channel = Image.new('L', target_size, 0)

            if g_img:
                if g_img.size != target_size:
                    g_img = g_img.resize(target_size, Image.LANCZOS)
                g_channel = g_img
            else:
                g_channel = Image.new('L', target_size, 0)

            if b_img:
                if b_img.size != target_size:
                    b_img = b_img.resize(target_size, Image.LANCZOS)
                b_channel = b_img
            else:
                b_channel = Image.new('L', target_size, 0)

            # 合并RGB通道
            rgb_img = Image.merge('RGB', (r_channel, g_channel, b_channel))

            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 根据格式保存
            self._save_image(rgb_img, output_path, output_format)

            self.processed_count += 1
            return True

        except Exception as e:
            self.failed_files.append((output_path, str(e)))
            return False

    def merge_rgb_files(self, color_files: list, r_files: list, g_files: list, b_files: list,
                        output_dir: str = None, output_format: str = 'PNG',
                        output_size: int = None, output_suffix: str = '_RAH',
                        progress_callback=None) -> dict:
        """
        批量合并RGB通道贴图

        Args:
            color_files: 彩色图文件路径列表（用作命名基础）
            r_files: R通道图文件路径列表（与color_files一一对应，None表示无匹配）
            g_files: G通道图文件路径列表（与color_files一一对应，None表示无匹配）
            b_files: B通道图文件路径列表（与color_files一一对应，None表示无匹配）
            output_dir: 输出目录（如果为空则使用各彩色图的源目录）
            output_format: 输出格式
            output_size: 输出尺寸（可选）
            output_suffix: 输出后缀（如_RAH）
            progress_callback: 进度回调函数 callback(current, total, filename)

        Returns:
            dict: 处理结果
        """
        self.processed_count = 0
        self.resized_count = 0
        self.failed_files = []
        self.skipped_files = []

        total = len(color_files)

        for idx, (color_file, r_file, g_file, b_file) in enumerate(zip(color_files, r_files, g_files, b_files), 1):
            filename = os.path.basename(color_file)
            name_no_ext = os.path.splitext(filename)[0]

            # 解析基础名称
            parsed = parse_texture_name(name_no_ext)
            base_name = parsed['base']

            # 确定输出目录
            if output_dir:
                target_dir = output_dir
            else:
                target_dir = os.path.dirname(color_file)

            # 检查是否至少有一个通道图
            if r_file is None and g_file is None and b_file is None:
                self.skipped_files.append(color_file)
                if progress_callback:
                    progress_callback(idx, total, filename)
                continue

            # 生成输出文件名
            ext = self._get_extension(output_format)
            if output_size:
                output_filename = f"{base_name}_{output_size}{output_suffix}{ext}"
            else:
                output_filename = f"{base_name}{output_suffix}{ext}"
            output_path = os.path.join(target_dir, output_filename)

            # 合并RGB通道
            self.merge_rgb_channels(r_file, g_file, b_file, output_path, output_format, output_size)

            # 进度回调
            if progress_callback:
                progress_callback(idx, total, filename)

        return {
            'success': self.processed_count,
            'resized': self.resized_count,
            'failed': len(self.failed_files),
            'skipped': len(self.skipped_files),
            'failed_files': self.failed_files,
            'skipped_files': self.skipped_files
        }
