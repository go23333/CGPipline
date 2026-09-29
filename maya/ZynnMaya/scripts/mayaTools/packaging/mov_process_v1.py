import json
import os
import platform
import shutil
import time
from moviepy.editor import VideoFileClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def get_heiti_font_path():
    """根据操作系统返回黑体字体路径"""
    system = platform.system()
    if system == "Windows":
        candidates = [
            "C:/Windows/Fonts/simhei.ttf",      # 黑体
            "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
        ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def add_multi_texts_safe(video_path, output_path, base_font_size=24, base_width=1920,
                         custom_font_path=None, margin=5, subtitle_data=None):
    """
    添加多位置文字，自动限制文字块不超出边缘20%的安全区，且所有文字使用统一字体大小
    margin: 文字与安全区边界的额外像素间距
    bottom_center_dynamic_list: 可选，中下第一行动态文本列表，索引0对应视频起始帧
    """
    bottom_center_dynamic_list = subtitle_data['bottomCenter2Text']
    video = VideoFileClip(video_path)
    fps = video.fps
    total_frames = int(video.duration * fps)
    width, height = video.size
    start_frame = int(subtitle_data['bottomRight2Text']) - 1  # 起始帧编号

    # 字体路径获取
    if custom_font_path and os.path.exists(custom_font_path):
        font_path = custom_font_path
    else:
        font_path = get_heiti_font_path()
        if font_path is None:
            print("警告: 未找到黑体字体，将使用默认字体")
        else:
            print(f"使用字体: {font_path}")

    init_font_size = int(base_font_size * (width / base_width))
    init_font_size = max(init_font_size, 12)

    try:
        if font_path:
            test_font = ImageFont.truetype(font_path, init_font_size)
        else:
            test_font = ImageFont.load_default()
    except:
        test_font = ImageFont.load_default()

    text_color = (255, 255, 255)
    line_spacing_ratio = 0.3

    # 静态文本配置（bottom_center 的第一行将在运行时动态替换）
    configs = {
        "top_left": {
            "text_lines": [subtitle_data['topLeftText'], subtitle_data['topLeft2Text']],
            "anchor": "lt",
            "safe_rect": (0.0, 0.0, 0.2, 0.2),
            "allow_overflow_h": False,
            "allow_overflow_v": False
        },
        "top_center": {
            "text_lines": [subtitle_data['topCenterText']],
            "anchor": "ct",
            "safe_rect": (0.0, 0.0, 1.0, 0.2),
            "allow_overflow_h": False,
            "allow_overflow_v": False
        },
        "top_right": {
            "text_lines": [subtitle_data['topRightText']],
            "anchor": "rt",
            "safe_rect": (0.8, 0.0, 1.0, 0.2),
            "allow_overflow_h": False,
            "allow_overflow_v": False
        },
        "bottom_left": {
            "text_lines": [subtitle_data['bottomLeft2Text'], subtitle_data['bottomLeftText']],
            "anchor": "lb",
            "safe_rect": (0.0, 0.8, 0.2, 1.0),
            "allow_overflow_h": False,
            "allow_overflow_v": False
        },
        "bottom_center": {
            "text_lines": [subtitle_data['bottomCenter2Text'], subtitle_data['bottomCenterText']],
            "anchor": "cb",
            "safe_rect": (0.0, 0.8, 1.0, 1.0),
            "allow_overflow_h": False,
            "allow_overflow_v": False,
            "dynamic_first_line": True   # 标记第一行需要动态替换
        },
        "bottom_right": {
            "text_lines": None,
            "anchor": "rb",
            "safe_rect": (0.8, 0.8, 1.0, 1.0),
            "allow_overflow_h": False,
            "allow_overflow_v": False,
            "dynamic": True
        }
    }

    # 辅助函数：计算多行文本的包围盒
    def get_text_bbox(draw, lines, font, line_spacing):
        max_width = 0
        total_height = 0
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            max_width = max(max_width, w)
            line_heights.append(h)
        total_height = sum(line_heights) + line_spacing * (len(lines)-1)
        return max_width, total_height, line_heights

    def fit_font_size(draw, lines, max_allowed_width, max_allowed_height, init_size, line_spacing_ratio):
        font_size = init_size
        best_size = 1
        for size in range(init_size, 0, -5):
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, size)
                else:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            line_spacing = int(size * line_spacing_ratio)
            w, h, _ = get_text_bbox(draw, lines, font, line_spacing)
            if w <= max_allowed_width and h <= max_allowed_height:      
                best_size = size
                break
        if best_size == 1:
            best_size = init_size
        return best_size

    # ---------- 统一字体大小计算（考虑动态列表的最长字符串）----------
    temp_img = Image.new('RGB', (width, height))
    temp_draw = ImageDraw.Draw(temp_img)

    max_fonts_per_region = []

    for key, cfg in configs.items():
        # 确定该区域的文本样本
        if key == "bottom_center" and bottom_center_dynamic_list:
            # 动态列表中的最长字符串 + 静态第二行
            # max_dynamic_str = max(bottom_center_dynamic_list, key=len) if bottom_center_dynamic_list else ""
            sample_lines = [cfg["text_lines"][0][1], cfg["text_lines"][1]]  # 第一行动态最长，第二行静态
        elif cfg.get("dynamic"):
            sample_lines = [str(total_frames), f"{total_frames}/{total_frames}"]
        else:
            sample_lines = cfg["text_lines"]

        sx_min, sy_min, sx_max, sy_max = cfg["safe_rect"]
        px_min = int(sx_min * width) + margin
        py_min = int(sy_min * height) + margin
        px_max = int(sx_max * width) - margin
        py_max = int(sy_max * height) - margin
        if px_max <= px_min:
            px_max = px_min + 1
        if py_max <= py_min:
            py_max = py_min + 1

        max_w = px_max - px_min
        max_h = py_max - py_min

        allowed_w = max_w if not cfg.get("allow_overflow_h", False) else width
        allowed_h = max_h if not cfg.get("allow_overflow_v", False) else height

        max_font = fit_font_size(temp_draw, sample_lines, allowed_w, allowed_h, init_font_size, line_spacing_ratio)
        max_fonts_per_region.append(max_font)
        print(f"{key} 单独最大字体: {max_font}")

    uniform_font_size = min(max_fonts_per_region)
    print(f"最终统一字体大小: {uniform_font_size}")

    def get_uniform_font():
        try:
            if font_path:
                return ImageFont.truetype(font_path, uniform_font_size)
            else:
                return ImageFont.load_default()
        except:
            return ImageFont.load_default()

    # 多行文本绘制函数
    def draw_multiline_safe(draw, lines, ref_x, ref_y, anchor, font, line_spacing, safe_rect_px):
        line_data = []
        max_width = 0
        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            line_data.append((w, h, line))
            max_width = max(max_width, w)
            total_height += h
        total_height += line_spacing * (len(lines) - 1)

        sx_min, sy_min, sx_max, sy_max = safe_rect_px

        if anchor == 'lt':
            base_left, base_top = ref_x, ref_y
        elif anchor == 'ct':
            base_left, base_top = ref_x - max_width//2, ref_y
        elif anchor == 'rt':
            base_left, base_top = ref_x - max_width, ref_y
        elif anchor == 'lb':
            base_left, base_top = ref_x, ref_y - total_height
        elif anchor == 'cb':
            base_left, base_top = ref_x - max_width//2, ref_y - total_height
        elif anchor == 'rb':
            base_left, base_top = ref_x - max_width, ref_y - total_height
        else:
            base_left, base_top = ref_x, ref_y

        if base_left < sx_min:
            base_left = sx_min
        if base_left + max_width > sx_max:
            base_left = sx_max - max_width
        if base_top < sy_min:
            base_top = sy_min
        if base_top + total_height > sy_max:
            base_top = sy_max - total_height

        current_y = base_top
        for (w, h, line) in line_data:
            if anchor in ('lt', 'lb'):
                line_left = base_left
            elif anchor in ('ct', 'cb'):
                line_left = base_left + (max_width - w) // 2
            else:
                line_left = base_left + (max_width - w)
            draw.text((line_left, current_y), line, fill=text_color, font=font)
            current_y += h + line_spacing

    # 帧处理函数
    def transform_frame(frame, t):
        current_frame = int(t * fps) + 1
        abs_frame = current_frame + start_frame   # 绝对帧号（用于动态文本索引）
        pil_img = Image.fromarray(frame)
        draw = ImageDraw.Draw(pil_img)
        font = get_uniform_font()
        line_spacing = int(uniform_font_size * line_spacing_ratio)

        for key, cfg in configs.items():
            sx_min, sy_min, sx_max, sy_max = cfg["safe_rect"]
            px_min = int(sx_min * width) + margin
            py_min = int(sy_min * height) + margin
            px_max = int(sx_max * width) - margin
            py_max = int(sy_max * height) - margin
            if px_max <= px_min:
                px_max = px_min + 1
            if py_max <= py_min:
                py_max = py_min + 1
            safe_rect_px = (px_min, py_min, px_max, py_max)

            # 确定当前文本内容
            if key == "bottom_center" and cfg.get("dynamic_first_line") and bottom_center_dynamic_list:
                # 动态第一行，静态第二行
                idx = abs_frame - 1  # 列表索引从0开始
                if 0 <= idx < len(bottom_center_dynamic_list):
                    dynamic_line = bottom_center_dynamic_list[idx]
                else:
                    dynamic_line = cfg["text_lines"][0][-1]  # 超出范围时使用列表最后一个文本
                lines = [dynamic_line, cfg["text_lines"][1]]
            elif cfg.get("dynamic"):
                lines = ['Frame:'+str(abs_frame), 'Sequence:'+f"{abs_frame}/{total_frames+start_frame}"]
            else:
                lines = cfg["text_lines"]

            anchor = cfg["anchor"]
            if anchor == 'lt':
                ref_x, ref_y = safe_rect_px[0], safe_rect_px[1]
            elif anchor == 'ct':
                ref_x, ref_y = (safe_rect_px[0] + safe_rect_px[2]) // 2, safe_rect_px[1]
            elif anchor == 'rt':
                ref_x, ref_y = safe_rect_px[2], safe_rect_px[1]
            elif anchor == 'lb':
                ref_x, ref_y = safe_rect_px[0], safe_rect_px[3]
            elif anchor == 'cb':
                ref_x, ref_y = (safe_rect_px[0] + safe_rect_px[2]) // 2, safe_rect_px[3]
            elif anchor == 'rb':
                ref_x, ref_y = safe_rect_px[2], safe_rect_px[3]
            else:
                ref_x, ref_y = safe_rect_px[0], safe_rect_px[1]

            draw_multiline_safe(draw, lines, ref_x, ref_y, anchor, font, line_spacing, safe_rect_px)

        return np.array(pil_img)

    final_clip = video.fl(lambda gf, t: transform_frame(gf(t), t))

    temp_audio_path = 'D:/temp_audio.m4a'
    if '.avi' in output_path:
        try:
            final_clip.write_videofile(output_path, codec='mpeg4', bitrate="10000k", audio_codec='aac',temp_audiofile=temp_audio_path)
        except:
            try:
                print('音频生成失败')
                time.sleep(2)
                final_clip.write_videofile(output_path, codec='mpeg4', bitrate="10000k", audio_codec='aac',audio=False)
            except:
                print('视频生成失败')
                time.sleep(2)
                    
    else:
        try:
            final_clip.write_videofile(output_path, codec='libx264', bitrate="10000k", audio_codec='aac',temp_audiofile=temp_audio_path)
        except:
            try:
                print('音频生成失败')
                time.sleep(2)
                final_clip.write_videofile(output_path, codec='libx264', bitrate="10000k", audio_codec='aac',audio=False)
            except:
                print('视频生成失败')
                time.sleep(2)
        
    video.close()
    final_clip.close()
    print("处理完成（统一字体大小，中下第一行动态）")


def start():
    json_data = ''
    if os.path.exists('D:/mov_data.json'):
        with open('D:/mov_data.json', 'r') as f:
            json_data = json.load(f)

    if json_data:
        old_view_video = json_data[0]
        new_view_video = old_view_video.replace('_oldView.', '.')
        new_view_video = new_view_video.replace('/mov_temp/', '/')
        subtitle_data = json_data[1]
        temp_file = old_view_video.rsplit('/',1)[0]


    # print(subtitle_data)
    add_multi_texts_safe(
        old_view_video,
        new_view_video,
        base_font_size=80,
        base_width=1920,
        margin=5,
        subtitle_data=subtitle_data
    )
    # 处理完成后删除临时文件夹
    if temp_file:
        shutil.rmtree(temp_file)
    if os.path.exists('D:/mov_data.json'):
        os.remove('D:/mov_data.json')



if __name__ == "__main__":
    start()
    #conda activate py397_1
    #pyinstaller -F --collect-all imageio --collect-all moviepy mov_process_v1.py
