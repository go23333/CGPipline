# -*- coding: utf-8 -*-
"""
特效自动录制模块

严格按以下步骤执行：
    1. 将 ThirdParty 渲染关卡依赖按需拷贝到 Content，确保 midSence 空关卡存在，并加载 B_Scene 关卡
    2. 把选中的资产加载到临时关卡中
    3. 创建一个临时关卡序列
    4. 打开刚才创建的临时关卡序列
    5. 调用 Quick Render（Use Viewport Camera in Sequence）进行渲染
    6. 把渲染输出目录下的图片转成视频
"""

import json
import os
import shutil
import subprocess
import time
import unreal

DEFAULT_FPS = 25
DEFAULT_DURATION_SECONDS = 8
DEFAULT_RESOLUTION_X = 1920
DEFAULT_RESOLUTION_Y = 1080
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = os.path.normpath(
    os.path.join(_SCRIPT_DIR, "..", "ThirdParty", "ffmpeg", "ffmpeg.exe")
)
THIRDPARTY_DIR = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "ThirdParty"))
_THIRDPARTY_SKIP = {"ffmpeg", "ffmpeg.exe"}
TEMP_CONTENT_DIR = "/Game/Temp"
MID_SCENE_GAME_PATH = "/Game/midSence"
RENDER_LEVEL_GAME_PATH = "/Game/VFX/Effects/B_Scene"
RENDER_LEVEL_CONTENT_SUBPATH = os.path.join("VFX", "Effects", "B_Scene.umap")
RENDER_LEVEL_SCAN_PATH = "/Game/VFX/Effects"
IMAGE_EXTENSIONS = (".jpeg", ".jpg", ".png")
WATCH_TIMEOUT_SEC = 180


def _content_dir() -> str:
    return unreal.Paths.project_content_dir()


def _render_level_disk_path() -> str:
    return os.path.join(_content_dir(), RENDER_LEVEL_CONTENT_SUBPATH)


def _normalize_path(path: str) -> str:
    """统一为正斜杠，避免 Y:/.../MovieRenders\\file.mp4 混用分隔符。"""
    return path.replace("\\", "/") if path else path


def _normalize_abs_path(path: str) -> str:
    return _normalize_path(os.path.abspath(os.path.normpath(path))) if path else path


def _game_path_from_content_name(name: str) -> str:
    asset_name = os.path.splitext(name)[0]
    return f"/Game/{asset_name}"


def _content_rel_from_game_path(game_path: str) -> str:
    if game_path.startswith("/Game/"):
        return game_path[6:]
    if game_path == "/Game":
        return ""
    return game_path.lstrip("/")


def _relative_to_game_path(rel_path: str) -> str:
    rel_path = rel_path.replace("\\", "/")
    asset_rel = os.path.splitext(rel_path)[0]
    return f"/Game/{asset_rel}"


def _frame_rate_as_float(rate) -> float:
    if rate is None:
        return 0.0
    denom = float(rate.denominator) if rate.denominator else 1.0
    return float(rate.numerator) / denom


def _display_frame_to_tick(seq, display_frame: int) -> int:
    """显示帧 → 序列 tick。AutomatedLevelSequenceCapture 的自定义帧是 tick，不是 25fps 显示帧。"""
    extensions = getattr(unreal, "MovieSceneSequenceExtensions", None)
    if not extensions:
        return int(display_frame)
    tick = extensions.get_tick_resolution(seq)
    display = extensions.get_display_rate(seq)
    tick_f = _frame_rate_as_float(tick)
    display_f = _frame_rate_as_float(display) or 1.0
    return int(round(float(display_frame) * tick_f / display_f))


def _set_capture_frame_range(capture, start_tick: int, end_tick: int):
    """写入 capture 自定义起止帧。必须是 tick（8s @ 24000 = 192000），不是显示帧 200。"""
    start_frame = int(start_tick)
    end_frame = int(end_tick)
    start_fn = unreal.FrameNumber(start_frame)
    end_fn = unreal.FrameNumber(end_frame)

    capture.use_custom_start_frame = True
    capture.use_custom_end_frame = True
    for prop_name, value in (
        ("use_custom_start_frame", True),
        ("use_custom_end_frame", True),
    ):
        try:
            capture.set_editor_property(prop_name, value)
        except Exception:
            pass

    applied = False
    for start_value, end_value in ((start_fn, end_fn), (start_frame, end_frame)):
        try:
            capture.custom_start_frame = start_value
            capture.custom_end_frame = end_value
            applied = True
            break
        except Exception:
            pass
        try:
            capture.set_editor_property("custom_start_frame", start_value)
            capture.set_editor_property("custom_end_frame", end_value)
            applied = True
            break
        except Exception:
            pass

    if not applied:
        try:
            capture.custom_start_frame = unreal.FrameNumber(0)
            capture.custom_end_frame = unreal.FrameNumber(0)
            capture.custom_start_frame.value = start_frame
            capture.custom_end_frame.value = end_frame
            applied = True
        except Exception:
            pass

    start_n = getattr(capture.custom_start_frame, "value", capture.custom_start_frame)
    end_n = getattr(capture.custom_end_frame, "value", capture.custom_end_frame)
    print(
        "[EffectRecorder]   Capture custom frame range: "
        f"{start_n} -> {end_n} "
        f"(use_custom={capture.use_custom_start_frame}/"
        f"{capture.use_custom_end_frame}, applied={applied})"
    )
    if not applied:
        print(
            f"[EffectRecorder]   警告: 无法写入 capture 自定义帧范围 "
            f"{start_frame} -> {end_frame}"
        )


def _get_sequence_playback_frame_count(seq, fps: int = DEFAULT_FPS) -> int:
    extensions = getattr(unreal, "MovieSceneSequenceExtensions", None)
    if not extensions:
        return -1
    try:
        if hasattr(extensions, "get_playback_start_seconds"):
            start_s = float(extensions.get_playback_start_seconds(seq))
            end_s = float(extensions.get_playback_end_seconds(seq))
            return max(0, int(round((end_s - start_s) * float(fps))))
        start = int(extensions.get_playback_start(seq))
        end = int(extensions.get_playback_end(seq))
        display = _frame_rate_as_float(extensions.get_display_rate(seq)) or float(fps)
        tick = _frame_rate_as_float(extensions.get_tick_resolution(seq)) or display
        return max(0, int(round((end - start) * display / tick)))
    except Exception:
        return -1


def _sequence_soft_object_path(seq) -> unreal.SoftObjectPath:
    """AutomatedLevelSequenceCapture 需要 ObjectPath（含 .AssetName）。"""
    object_path = seq.get_path_name()
    if "." not in object_path.rsplit("/", 1)[-1]:
        object_path = f"{object_path}.{seq.get_name()}"
    return unreal.SoftObjectPath(object_path)


def _set_sequence_time_ranges(seq, fps: int, total_frames: int):
    """
    用「秒」设置播放范围，不要改 tick resolution。

    UE 默认 tick 是 24000。把 tick 改成 25 后，Python 里 playback 看起来是 0~200，
    但 SequencerTools.render_movie 进 PIE 仍按 24000 tick 读自定义帧：
    custom_end_frame=200 tick ≈ 0.008 秒，随后退回默认约 1 秒（~30 张图）。
    """
    duration_seconds = float(total_frames) / float(fps)
    frame_rate = unreal.FrameRate(fps, 1)
    extensions = getattr(unreal, "MovieSceneSequenceExtensions", None)

    if extensions:
        extensions.set_display_rate(seq, frame_rate)
        if hasattr(extensions, "set_playback_start_seconds"):
            extensions.set_playback_start_seconds(seq, 0.0)
            extensions.set_playback_end_seconds(seq, duration_seconds)
        else:
            start_tick = _display_frame_to_tick(seq, 0)
            end_tick = _display_frame_to_tick(seq, total_frames)
            extensions.set_playback_start(seq, start_tick)
            extensions.set_playback_end(seq, end_tick)
        try:
            extensions.set_work_range_start(seq, 0.0)
            extensions.set_work_range_end(seq, duration_seconds)
            extensions.set_view_range_start(seq, 0.0)
            extensions.set_view_range_end(seq, duration_seconds)
        except Exception:
            pass
        for loop_name in ("set_loop_playback",):
            fn = getattr(seq, loop_name, None)
            if fn:
                try:
                    fn(False)
                except Exception:
                    pass
        try:
            movie_scene = seq.get_movie_scene()
            if movie_scene and hasattr(movie_scene, "set_playback_range_locked"):
                movie_scene.set_playback_range_locked(True)
        except Exception:
            pass

        try:
            start_s = (
                extensions.get_playback_start_seconds(seq)
                if hasattr(extensions, "get_playback_start_seconds")
                else None
            )
            end_s = (
                extensions.get_playback_end_seconds(seq)
                if hasattr(extensions, "get_playback_end_seconds")
                else None
            )
            rate = extensions.get_display_rate(seq)
            tick = extensions.get_tick_resolution(seq)
            got_frames = (
                int(round((float(end_s) - float(start_s)) * float(fps)))
                if start_s is not None and end_s is not None
                else _get_sequence_playback_frame_count(seq, fps)
            )
            print(
                f"[EffectRecorder]   Sequence playback verified: "
                f"{start_s}s -> {end_s}s ({got_frames} 帧), "
                f"display {rate.numerator}/{rate.denominator}, "
                f"tick {tick.numerator}/{tick.denominator}, "
                f"raw_end={int(extensions.get_playback_end(seq))}"
            )
            if got_frames != total_frames:
                print(
                    f"[EffectRecorder]   警告: 期望长度 {total_frames} 帧，"
                    f"实际 {got_frames} 帧"
                )
        except Exception as e:
            print(f"[EffectRecorder]   无法校验 playback range: {e}")
        return

    seq.set_display_rate(frame_rate)
    seq.set_playback_start(0)
    seq.set_playback_end(total_frames)
    for fn_name, value in (
        ("set_work_range_start", 0.0),
        ("set_work_range_end", duration_seconds),
        ("set_view_range_start", 0.0),
        ("set_view_range_end", duration_seconds),
    ):
        fn = getattr(seq, fn_name, None)
        if fn:
            fn(value)


def _set_section_frame_range(section, start_frame: int, end_frame: int, fps: int = None, seq=None):
    """Camera Cut / Transform section 用秒或 tick 拉满，不要把显示帧 200 当成 tick 写入。"""
    start_frame = int(start_frame)
    end_frame = int(end_frame)
    start_seconds = None
    end_seconds = None
    if fps and fps > 0:
        start_seconds = float(start_frame) / float(fps)
        end_seconds = float(end_frame) / float(fps)

    extensions = getattr(unreal, "MovieSceneSectionExtensions", None)
    applied_seconds = False
    if extensions and start_seconds is not None:
        try:
            extensions.set_range_seconds(section, start_seconds, end_seconds)
            applied_seconds = True
        except Exception:
            try:
                extensions.set_start_frame_seconds(section, start_seconds)
                extensions.set_end_frame_seconds(section, end_seconds)
                applied_seconds = True
            except Exception:
                pass

    if not applied_seconds:
        start_tick = (
            _display_frame_to_tick(seq, start_frame) if seq else start_frame
        )
        end_tick = _display_frame_to_tick(seq, end_frame) if seq else end_frame
        if extensions:
            try:
                if hasattr(extensions, "set_range"):
                    extensions.set_range(section, start_tick, end_tick)
            except Exception:
                try:
                    extensions.set_start_frame_bounded(section, start_tick)
                    extensions.set_end_frame_bounded(section, end_tick)
                except Exception:
                    pass
        for start_value, end_value in (
            (start_tick, end_tick),
            (unreal.FrameNumber(start_tick), unreal.FrameNumber(end_tick)),
        ):
            if hasattr(section, "set_range"):
                try:
                    section.set_range(start_value, end_value)
                    break
                except Exception:
                    pass
            try:
                section.set_start_frame(start_value)
                section.set_end_frame(end_value)
                break
            except Exception:
                pass

    verified = None
    if extensions and start_seconds is not None:
        try:
            verified = (
                float(extensions.get_start_frame_seconds(section)),
                float(extensions.get_end_frame_seconds(section)),
            )
        except Exception:
            pass
    if verified is None and extensions:
        try:
            verified = (
                int(extensions.get_start_frame(section)),
                int(extensions.get_end_frame(section)),
            )
        except Exception:
            pass

    print(f"[EffectRecorder]   Section range set -> verified={verified}")
    if verified is not None and fps:
        if isinstance(verified[0], float):
            got_frames = int(round((verified[1] - verified[0]) * float(fps)))
        else:
            got_frames = -1
        expect = end_frame - start_frame
        if got_frames >= 0 and got_frames < expect:
            print(
                f"[EffectRecorder]   警告: section 实际只有 {got_frames} 帧，"
                f"期望 {expect}；拍屏会被裁切到这个长度"
            )
    return verified


def _extend_binding_with_transform(
    binding, start_frame: int, end_frame: int, fps: int, location, seq=None
):
    """
    给 binding 加贯穿全长的 Transform track + 首尾关键，
    强制「序列内容范围」拉到 total_frames（capture 会按内容裁切）。
    """
    try:
        track = binding.add_track(unreal.MovieScene3DTransformTrack)
    except Exception:
        try:
            track = unreal.MovieSceneBindingExtensions.add_track(
                binding, unreal.MovieScene3DTransformTrack
            )
        except Exception as e:
            print(f"[EffectRecorder]   无法添加 Transform track: {e}")
            return

    section = track.add_section()
    _set_section_frame_range(section, start_frame, end_frame, fps=fps, seq=seq)

    extensions = getattr(unreal, "MovieSceneSectionExtensions", None)
    if not extensions or not hasattr(extensions, "get_all_channels"):
        return

    try:
        channels = extensions.get_all_channels(section)
    except Exception as e:
        print(f"[EffectRecorder]   无法获取 transform channels: {e}")
        return

    loc = (float(location.x), float(location.y), float(location.z))
    defaults = list(loc) + [0.0, 0.0, 0.0] + [1.0, 1.0, 1.0]
    start_tick = _display_frame_to_tick(seq, start_frame) if seq else start_frame
    end_tick = _display_frame_to_tick(seq, end_frame) if seq else end_frame
    for frame in (start_tick, max(start_tick, end_tick - 1)):
        frame_number = unreal.FrameNumber(int(frame))
        for i, value in enumerate(defaults):
            if i >= len(channels):
                break
            try:
                channels[i].add_key(frame_number, value)
            except Exception:
                try:
                    channels[i].add_key(frame_number, float(value), 0.0, 0)
                except Exception:
                    pass
    print(
        f"[EffectRecorder]   Transform track 已拉通: "
        f"display {start_frame}->{end_frame}, tick {start_tick}->{end_tick}"
    )


def _iter_thirdparty_asset_files():
    """遍历 ThirdParty 下所有 UE 资产文件，yield (src_path, content_rel_path)。"""
    for root, dirs, files in os.walk(THIRDPARTY_DIR):
        dirs[:] = [
            d for d in dirs if d not in _THIRDPARTY_SKIP and not d.startswith(".")
        ]
        for name in files:
            if name in _THIRDPARTY_SKIP or not name.lower().endswith(
                (".uasset", ".umap")
            ):
                continue
            src_path = os.path.join(root, name)
            rel_path = os.path.relpath(src_path, THIRDPARTY_DIR)
            yield src_path, rel_path


def _should_copy_file(src_path: str, dest_path: str) -> bool:
    """仅在目标不存在，或大小/修改时间不一致时拷贝，避免重复写盘触发编辑器脏标记。"""
    if not os.path.isfile(dest_path):
        return True
    try:
        return (
            os.path.getsize(src_path) != os.path.getsize(dest_path)
            or int(os.path.getmtime(src_path)) != int(os.path.getmtime(dest_path))
        )
    except OSError:
        return True


def _copy_thirdparty_to_content() -> list[str]:
    """将 ThirdParty 下 UE 资产按需拷贝到 Content，返回对应 /Game 路径（供清理）。"""
    if not os.path.isdir(THIRDPARTY_DIR):
        raise FileNotFoundError(f"找不到 ThirdParty 目录: {THIRDPARTY_DIR}")

    content_dir = _content_dir()
    copied_paths = []
    copied_count = 0
    skipped_count = 0

    for src_path, rel_path in _iter_thirdparty_asset_files():
        dest_path = os.path.join(content_dir, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        game_path = _relative_to_game_path(rel_path)
        copied_paths.append(game_path)

        if _should_copy_file(src_path, dest_path):
            shutil.copy2(src_path, dest_path)
            copied_count += 1
            print(f"[EffectRecorder]   已拷贝文件: {src_path} -> {dest_path}")
        else:
            skipped_count += 1
            print(f"[EffectRecorder]   已存在，跳过: {dest_path}")

    if not copied_paths:
        raise FileNotFoundError(f"ThirdParty 下没有可拷贝的 UE 资产: {THIRDPARTY_DIR}")

    print(
        f"[EffectRecorder]   ThirdParty 拷贝完成: "
        f"写入 {copied_count}，跳过 {skipped_count}"
    )
    return copied_paths


def _delete_copied_game_path(game_path: str):
    """删除单个拷贝资产，仅删除本次记录的具体文件，不删整个目录。"""
    if unreal.EditorAssetLibrary.does_asset_exist(game_path):
        unreal.EditorAssetLibrary.delete_asset(game_path)
        print(f"[EffectRecorder]   ✓ 已删除资产: {game_path}")
        return

    rel_path = _content_rel_from_game_path(game_path)
    disk_base = os.path.join(_content_dir(), rel_path)
    removed = False
    for ext in (".umap", ".uasset"):
        file_path = disk_base + ext
        if os.path.isfile(file_path):
            os.remove(file_path)
            removed = True
            print(f"[EffectRecorder]   ✓ 已删除磁盘文件: {file_path}")

    if not removed:
        print(f"[EffectRecorder]   未找到可删除项: {game_path}")


def _ensure_mid_scene_level():
    """确保 Content 根目录存在空的 midSence 关卡；已存在则复用。"""
    if unreal.EditorAssetLibrary.does_asset_exist(MID_SCENE_GAME_PATH):
        print(f"[EffectRecorder]   复用现有关卡: {MID_SCENE_GAME_PATH}")
        return

    print(f"[EffectRecorder]   创建空关卡: {MID_SCENE_GAME_PATH}")
    level = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name="midSence",
        package_path="/Game",
        asset_class=unreal.World,
        factory=unreal.WorldFactory(),
    )
    if not level:
        raise RuntimeError(f"创建关卡失败: {MID_SCENE_GAME_PATH}")

    unreal.EditorAssetLibrary.save_loaded_asset(level)
    print(f"[EffectRecorder]   空关卡已创建: {MID_SCENE_GAME_PATH}")


# MovieGraphQuickRenderSubsystem 仅 UE 5.4+ 提供；5.3 上设为 None，避免模块导入时报错
if hasattr(unreal, "MovieGraphQuickRenderSubsystem"):
    quick_subsystem = unreal.get_editor_subsystem(unreal.MovieGraphQuickRenderSubsystem)
else:
    quick_subsystem = None

# 全局 tick 句柄，避免第二次运行时旧回调未注销导致崩溃
_active_watch_handle = None
_deferred_handle = None
_recorder_instance = None
_is_recording = False


def _stop_folder_watch():
    global _active_watch_handle
    if _active_watch_handle is not None:
        try:
            unreal.unregister_slate_post_tick_callback(_active_watch_handle)
        except Exception:
            pass
        _active_watch_handle = None


def _stop_deferred():
    global _deferred_handle
    if _deferred_handle is not None:
        try:
            unreal.unregister_slate_post_tick_callback(_deferred_handle)
        except Exception:
            pass
        _deferred_handle = None


def stop_all_callbacks():
    """reload 或重新打开工具前调用，注销所有 Slate 回调。"""
    global _is_recording
    _stop_folder_watch()
    _stop_deferred()
    _is_recording = False


def _defer_next_tick(callback):
    """下一帧再执行，避免在 Slate Tick 内调 UE API / 删资产导致崩溃。"""
    global _deferred_handle
    _stop_deferred()

    def _once(_dt):
        global _deferred_handle
        if _deferred_handle is not None:
            try:
                unreal.unregister_slate_post_tick_callback(_deferred_handle)
            except Exception:
                pass
            _deferred_handle = None
        callback()

    _deferred_handle = unreal.register_slate_post_tick_callback(_once)


def _defer_cleanup_chain(steps):
    """按顺序跨多帧执行清理步骤，降低 UE 编辑器崩溃风险。"""
    if not steps:
        return

    def run_step(index=0):
        if index >= len(steps):
            return
        try:
            steps[index]()
        except Exception as e:
            print(f"[EffectRecorder]   清理步骤 {index + 1} 失败: {e}")
        _defer_next_tick(lambda: run_step(index + 1))

    _defer_next_tick(lambda: run_step(0))


class EffectRecorder:
    def __init__(self):
        self._temp_scene_dir = TEMP_CONTENT_DIR
        self._temp_level_path = RENDER_LEVEL_GAME_PATH
        self._temp_seq_path = "/Game/Temp/EffectCaptureSeq"
        self._effect_actor = None
        self._temp_level_actors = []
        self._render_viewport = None
        self._watch_tick_fn = None  # 防止 GC 回收 tick 回调
        self._active_capture = None
        self._render_callback = None
        self._copied_content_paths = []
        self._needs_cleanup = False

    def record(
        self,
        effect_asset,
        asset_list,
        fps: int = DEFAULT_FPS,
        duration_seconds: float = DEFAULT_DURATION_SECONDS,
    ) -> str:
        global _is_recording
        if _is_recording:
            print("[EffectRecorder] 已有录制进行中，跳过本次请求")
            return None

        _is_recording = True
        _stop_folder_watch()
        self._clear_mrq_state()
        self._copied_content_paths = []
        self._needs_cleanup = False
        self._finish_started = False

        # try:
        # load_level 后原 UObject 引用常会失效，先记下路径，第二步再重新 load。
        asset_path = effect_asset.get_path_name()
        asset_name = effect_asset.get_name()
        self._step1_create_temp_level()
        print(f"第一步：拷贝渲染关卡依赖到 Content 并加载 B_Scene 关卡")

        self._effect_actor = self._step2_load_asset_to_level(asset_path)
        print(f"加载资产到关卡里")

        unreal.EditorLevelLibrary.save_current_level()
        print(f"第二步：加载资产到关卡里并保存")

        total_frames = max(1, int(fps * duration_seconds))
        seq = self._step3_create_temp_sequence(fps, total_frames, self._effect_actor)
        self._step4_open_temp_sequence(seq, fps, total_frames)
        self._step5_quick_render_viewport_camera(
            seq, total_frames, asset_name, fps, asset_list
        )
        #     return
        # except Exception as e:
        #     print(f"[EffectRecorder] 异常: {e}")
        #     if self._needs_cleanup:
        #         self._clear_mrq_state()
        #         self._schedule_cleanup()
        #     _is_recording = False
        #     raise

    # ----------------------------------------------------------------
    # 第一步：拷贝渲染关卡依赖到 Content 并加载 B_Scene 关卡
    # ----------------------------------------------------------------

    def _step1_create_temp_level(self):
        """
        1. 将 ThirdParty 渲染关卡依赖按需拷贝到 Content（已存在且一致则跳过）
        2. 确保 /Game/midSence 空关卡存在
        3. 扫描并加载 Content/VFX/Effects/B_Scene.umap（不强制保存整目录）
        """
        print("[EffectRecorder] 第一步：拷贝渲染关卡依赖到 Content 并加载关卡")
        if not os.path.isdir(THIRDPARTY_DIR):
            raise FileNotFoundError(f"找不到 ThirdParty 目录: {THIRDPARTY_DIR}")

        self._copied_content_paths = _copy_thirdparty_to_content()
        self._needs_cleanup = True
        _ensure_mid_scene_level()

        level_disk_path = _render_level_disk_path()
        if not os.path.isfile(level_disk_path):
            raise FileNotFoundError(f"找不到关卡文件: {level_disk_path}")

        # 只扫描渲染关卡及其依赖目录，让 Asset Registry 认到磁盘上的新文件。
        # 不要 save_directory(only_if_is_dirty=False)：那会强制重写整棵
        # /Game/VFX/Effects，把无关资产也拖进保存/内存。
        # 也不要扫整个 /Game/VFX，以免把 effectsLibrary 一并 force_rescan。
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        asset_registry.scan_paths_synchronous(
            [RENDER_LEVEL_SCAN_PATH, "/Game/VFX/Common"],
            force_rescan=True,
        )

        if not unreal.EditorAssetLibrary.does_asset_exist(self._temp_level_path):
            raise RuntimeError(f"关卡未注册: {self._temp_level_path}")

        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(
            self._temp_level_path
        )
        print(f"[EffectRecorder]   关卡已加载: {self._temp_level_path}")

    # ----------------------------------------------------------------
    # 第二步：把选中的资产加载到临时关卡中
    # ----------------------------------------------------------------

    def _reload_effect_asset(self, effect_asset_or_path):
        """切关卡后重新加载特效资产，避免持有失效的 UObject 引用。"""
        if isinstance(effect_asset_or_path, str):
            object_path = effect_asset_or_path
        else:
            object_path = effect_asset_or_path.get_path_name()

        package_path = object_path.split(".", 1)[0]
        effect_asset = unreal.EditorAssetLibrary.load_asset(package_path)
        if not effect_asset:
            raise RuntimeError(f"无法加载特效资产: {package_path}")
        return effect_asset, package_path

    def _step2_load_asset_to_level(self, effect_asset_or_path) -> unreal.Actor:
        effect_asset, package_path = self._reload_effect_asset(effect_asset_or_path)
        print(
            f"[EffectRecorder] 第二步：加载资产到临时关卡 -> "
            f"{effect_asset.get_name()} ({package_path})"
        )

        editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        self._temp_level_actors = []
        asset_class_name = effect_asset.get_class().get_name()
        spawn_loc = unreal.Vector(0, 0, 50)
        spawn_rot = unreal.Rotator(0, 0, 0)

        if asset_class_name == "NiagaraSystem":
            actor = editor_subsystem.spawn_actor_from_class(
                unreal.NiagaraActor, spawn_loc, spawn_rot
            )
            if not actor:
                raise RuntimeError("生成 NiagaraActor 失败")
            comp = actor.get_component_by_class(unreal.NiagaraComponent)
            if not comp:
                raise RuntimeError("NiagaraActor 上找不到 NiagaraComponent")
            comp.set_asset(effect_asset)
            # 确认 set_asset 生效（失效引用时这里仍会是空）
            bound = comp.get_asset() if hasattr(comp, "get_asset") else None
            if not bound:
                raise RuntimeError(
                    f"NiagaraComponent.set_asset 失败，资产未绑定: {package_path}"
                )
            comp.activate(True)
            if hasattr(comp, "reinitialize_system"):
                comp.reinitialize_system()
            elif hasattr(comp, "reset_system"):
                comp.reset_system()
        elif asset_class_name == "ParticleSystem":
            actor = editor_subsystem.spawn_actor_from_class(
                unreal.Actor, spawn_loc, spawn_rot
            )
            if not actor:
                raise RuntimeError("生成 Particle Actor 失败")
            comp = actor.add_component_by_class(
                unreal.ParticleSystemComponent, False, unreal.Transform(), False
            )
            if not comp:
                raise RuntimeError("添加 ParticleSystemComponent 失败")
            comp.set_template(effect_asset)
            if hasattr(comp, "set_editor_property"):
                try:
                    comp.set_editor_property("template", effect_asset)
                except Exception:
                    pass
            if not comp.template:
                raise RuntimeError(
                    f"ParticleSystemComponent.set_template 失败: {package_path}"
                )
            actor.set_root_component(comp)
            comp.activate(True)
        else:
            raise ValueError(f"不支持的资产类型: {asset_class_name}")

        # B_Scene 自带灯光时这两盏是兜底；生成失败不阻断主流程
        light_actor = editor_subsystem.spawn_actor_from_class(
            unreal.DirectionalLight,
            unreal.Vector(0, 0, 500),
            unreal.Rotator(-50, 30, 0),
        )
        sky_actor = editor_subsystem.spawn_actor_from_class(
            unreal.SkyLight,
            unreal.Vector(0, 0, 600),
            unreal.Rotator(0, 0, 0),
        )

        actor.set_actor_label(f"_TempEffect_{effect_asset.get_name()}")
        self._temp_level_actors = [
            a for a in (actor, light_actor, sky_actor) if a is not None
        ]
        print(
            f"[EffectRecorder]   资产已放入关卡: {actor.get_actor_label()} "
            f"@ {spawn_loc.x},{spawn_loc.y},{spawn_loc.z} "
            f"类型={asset_class_name}"
        )
        return actor

    # ----------------------------------------------------------------
    # 第三步：创建一个临时关卡序列
    # ----------------------------------------------------------------

    def _step3_create_temp_sequence(
        self, fps: int, total_frames: int, effect_actor: unreal.Actor
    ) -> unreal.LevelSequence:
        print("[EffectRecorder] 第三步：创建临时关卡序列")

        seq_dir = "/Game/Temp"
        if unreal.EditorAssetLibrary.does_asset_exist(self._temp_seq_path):
            unreal.EditorAssetLibrary.delete_asset(self._temp_seq_path)

        seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset_name="EffectCaptureSeq",
            package_path=seq_dir,
            asset_class=unreal.LevelSequence,
            factory=unreal.LevelSequenceFactoryNew(),
        )
        _set_sequence_time_ranges(seq, fps, total_frames)
        print(
            f"[EffectRecorder]   Sequence range: 0 ~ {total_frames - 1} frames, "
            f"{total_frames / fps:.2f}s @ {fps}fps"
        )
        seq.add_possessable(effect_actor)

        # --- 相机设置：生成相机 → 加入序列 → 设为 Camera Cut ---
        editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        camera_loc = unreal.Vector(-1200, 0, 0)
        camera_actor = editor_subsystem.spawn_actor_from_class(
            unreal.CineCameraActor,
            camera_loc,
            unreal.Rotator(0, 0, 0),
        )
        camera_binding = seq.add_possessable(camera_actor)

        # Camera Cut 必须覆盖全长；否则 capture 即使设了 0~200 也会被内容范围裁到 ~30 帧
        camera_cut_tracks = seq.find_tracks_by_type(unreal.MovieSceneCameraCutTrack)
        camera_cut_track = (
            camera_cut_tracks[0]
            if camera_cut_tracks
            else seq.add_track(unreal.MovieSceneCameraCutTrack)
        )
        camera_cut_section = camera_cut_track.add_section()
        _set_section_frame_range(camera_cut_section, 0, total_frames, fps=fps, seq=seq)

        camera_binding_id = unreal.MovieSceneObjectBindingID()
        camera_binding_id.set_editor_property("guid", camera_binding.get_id())
        camera_cut_section.set_camera_binding_id(camera_binding_id)

        # 再加一条贯穿全长的 Transform，确保「内容范围」= playback 范围
        _extend_binding_with_transform(
            camera_binding, 0, total_frames, fps, camera_loc, seq=seq
        )

        self._temp_level_actors.append(camera_actor)
        print(
            f"[EffectRecorder]   相机已加入序列并设为 Camera Cut: "
            f"{camera_actor.get_actor_label()} @ x=-1200"
        )

        unreal.EditorLevelLibrary.save_current_level()
        unreal.EditorAssetLibrary.save_loaded_asset(seq)

        print(f"[EffectRecorder]   临时关卡序列已创建: {self._temp_seq_path}")
        return seq

    # ----------------------------------------------------------------
    # 第四步：打开刚才创建的临时关卡序列
    # ----------------------------------------------------------------

    def _step4_open_temp_sequence(self, seq: unreal.LevelSequence, fps: int, total_frames: int):
        print("[EffectRecorder] 第四步：打开临时关卡序列")

        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
        current = (
            unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        )
        if not current:
            raise RuntimeError("Sequencer 未打开 Level Sequence")
        # 打开 Sequencer 后 UI 可能把范围打回默认 1 秒，再写一遍
        _set_sequence_time_ranges(current, fps, total_frames)
        lib = unreal.LevelSequenceEditorBlueprintLibrary
        for fn_name, value in (
            ("set_playback_start", 0),
            ("set_playback_end", total_frames),
        ):
            fn = getattr(lib, fn_name, None)
            if fn:
                try:
                    fn(value)
                except Exception:
                    pass
        unreal.EditorAssetLibrary.save_loaded_asset(current)
        print(f"[EffectRecorder]   序列已打开: {seq.get_path_name()}")

    def _count_images(self, folder: str) -> int:
        if not os.path.isdir(folder):
            return 0
        n = 0
        for root, _, files in os.walk(folder):
            for f in files:
                if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS:
                    n += 1
        return n

    def _clear_mrq_state(self):
        try:
            mrq = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
            executor = mrq.get_active_executor()
            if executor:
                for fn_name in ("cancel_all_jobs", "cancel"):
                    fn = getattr(executor, fn_name, None)
                    if fn:
                        fn()
                        break
            queue = mrq.get_queue()
            if queue:
                queue.delete_all_jobs()
        except Exception:
            pass

    def _watch_folder(
        self,
        folder: str,
        asset_name: str,
        fps: int,
        asset_list: list,
        expected_images: int = 0,
        on_done=None,
    ):
        """异步监听文件夹，0.5s 查一次，2s 无变化则打日志并停止。"""
        global _active_watch_handle
        _stop_folder_watch()

        state = {
            "count": self._count_images(folder),
            "last_change": time.time(),
            "start": time.time(),
            "acc": 0.0,
            "done": False,
            "expected_images": expected_images,
        }

        def on_tick(dt):
            if state["done"]:
                return

            state["acc"] += dt
            if state["acc"] < 0.5:
                return
            state["acc"] = 0

            n = self._count_images(folder)
            now = time.time()
            if (
                state["expected_images"] > 0
                and n >= state["expected_images"]
            ):
                state["done"] = True
                _stop_folder_watch()
                print(
                    f"[EffectRecorder]   已拍到 {n} 张（期望 "
                    f"{state['expected_images']}），结束捕获"
                )
                try:
                    unreal.EditorLevelLibrary.editor_end_play()
                except Exception as e:
                    print(f"[EffectRecorder]   editor_end_play 失败: {e}")
                return
            if n != state["count"]:
                print(f"[EffectRecorder]   文件数量: {state['count']} -> {n}")
                state["count"] = n
                state["last_change"] = now
            elif (
                n > 0
                and now - state["last_change"] >= 5.0
                and (state["expected_images"] <= 0 or n >= state["expected_images"])
            ):
                state["done"] = True
                _stop_folder_watch()
                print(f"[EffectRecorder]   2s 无变化，当前 {n} 个，监听结束")
                _defer_next_tick(
                    lambda: self._finish_after_render(
                        asset_name, fps, asset_list, on_done
                    )
                )
            elif now - state["start"] >= WATCH_TIMEOUT_SEC:
                state["done"] = True
                _stop_folder_watch()
                print(
                    f"[EffectRecorder]   监听超时 ({WATCH_TIMEOUT_SEC}s)，当前 {n} 个"
                )
                _defer_next_tick(
                    lambda: self._finish_after_render(
                        asset_name, fps, asset_list, on_done
                    )
                )

        self._watch_tick_fn = on_tick
        _active_watch_handle = unreal.register_slate_post_tick_callback(on_tick)
        print(f"[EffectRecorder]   监听目录: {folder} (当前 {state['count']} 个)")

    def _finish_after_render(
        self, asset_name: str, fps: int, asset_list: list, on_done=None
    ):
        global _is_recording
        if getattr(self, "_finish_started", False):
            return
        self._finish_started = True
        _stop_folder_watch()
        try:
            video_path = self._step6_images_to_video(asset_name, fps)
            if video_path:
                print(f"[EffectRecorder] 全部流程完成，视频: {video_path}")
                asset_list[0]["previewVideo"] = video_path
                upload_effect(asset_list)
            else:
                print("[EffectRecorder] 流程完成，但视频生成失败")
            if on_done:
                on_done(video_path)
        finally:
            self._clear_mrq_state()
            self._schedule_cleanup()
            self._active_capture = None
            self._render_callback = None
            _is_recording = False

    # ----------------------------------------------------------------
    # 第五步：Quick Render（Use Viewport Camera in Sequence）
    # ----------------------------------------------------------------
    def _step5_quick_render_viewport_camera(
        self,
        seq: unreal.LevelSequence,
        total_frames: int,
        asset_name: str,
        fps: int,
        asset_list: list,
    ):
        print("创建旧版关卡序列捕获实例）")
        # 渲染前再确认一次：打开 Sequencer 后范围仍在
        playback_frames = _get_sequence_playback_frame_count(seq, fps)
        if playback_frames > 0 and playback_frames != total_frames:
            print(
                f"[EffectRecorder]   渲染前发现序列长度 {playback_frames} != {total_frames}，重新写入"
            )
            _set_sequence_time_ranges(seq, fps, total_frames)
            unreal.EditorAssetLibrary.save_loaded_asset(seq)
        elif playback_frames == total_frames:
            print(f"[EffectRecorder]   渲染前序列长度确认: {playback_frames} 帧")

        capture = unreal.AutomatedLevelSequenceCapture()
        if hasattr(capture, "use_separate_process"):
            capture.use_separate_process = False

        # 2. 绑定关卡序列资产路径
        soft_path = _sequence_soft_object_path(seq)
        capture.level_sequence_asset = soft_path
        print(f"[EffectRecorder]   Capture sequence: {soft_path}")

        movie_capture_dir = os.path.join(
            unreal.Paths.project_saved_dir(), "MovieRenders"
        )
        print(f"movie_capture_dir: {movie_capture_dir}")
        if os.path.isdir(movie_capture_dir):
            for root, _, filenames in os.walk(movie_capture_dir):
                for name in filenames:
                    if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
                        try:
                            os.remove(os.path.join(root, name))
                        except OSError:
                            pass

        # AutomatedLevelSequenceCapture 是 config 类，必须改它自己的 settings，
        # 不要 new 一个 MovieSceneCaptureSettings 整份替换（帧率经常被 UI/ini 盖掉）。
        cap_settings = capture.settings
        cap_settings.output_directory = unreal.DirectoryPath(movie_capture_dir)
        cap_settings.use_custom_frame_rate = True
        cap_settings.custom_frame_rate = unreal.FrameRate(fps, 1)
        cap_settings.handle_frames = 0
        if hasattr(cap_settings, "use_relative_frame_numbers"):
            cap_settings.use_relative_frame_numbers = False
        capture.set_editor_property("settings", cap_settings)
        capture.set_image_capture_protocol_type(unreal.ImageSequenceProtocol_PNG)
        capture.warm_up_frame_count = 0
        for delay_prop in (
            "delay_before_warm_up",
            "delay_before_shot_warm_up",
            "delay_every_frame",
        ):
            if hasattr(capture, delay_prop):
                try:
                    setattr(capture, delay_prop, 0.0)
                except Exception:
                    pass

        start_tick = _display_frame_to_tick(seq, 0)
        end_tick = _display_frame_to_tick(seq, total_frames)
        applied_rate = capture.settings.custom_frame_rate
        print(
            f"[EffectRecorder]   Capture fps="
            f"{applied_rate.numerator}/{applied_rate.denominator}, "
            f"use_custom_fps={capture.settings.use_custom_frame_rate}, "
            f"显示帧 0->{total_frames} => tick {start_tick}->{end_tick}"
        )
        # custom_end_frame 与 MovieScene PlaybackRange 一样是 tick。
        # 写 200 会变成 200/24000 秒，再退回默认 1 秒 ≈ 33 张。
        _set_capture_frame_range(capture, start_tick, end_tick)
        print(
            f"[EffectRecorder]   期望输出 {total_frames} 帧 @ {fps}fps"
        )

        # 4. 渲染完成回调
        def render_finish(success: bool):
            current_count = self._count_images(movie_capture_dir)
            print(
                f"[EffectRecorder] 捕获停止 success={success}, "
                f"当前图片数={current_count}, 期望={total_frames}"
            )
            self._finish_after_render(asset_name, fps, asset_list, on_done=None)

        self._active_capture = capture
        self._render_callback = unreal.OnRenderMovieStopped()
        self._render_callback.bind_callable(render_finish)

        # 5. 执行旧版影片场景捕获（核心调用）
        unreal.SequencerTools.render_movie(capture, self._render_callback)
        print("[EffectRecorder]   第五步：已开始 SequencerTools.render_movie")
        self._watch_folder(
            movie_capture_dir,
            asset_name,
            fps,
            asset_list,
            expected_images=total_frames,
        )

    # ----------------------------------------------------------------
    # 第六步：把 MovieRenders 目录下的图片转成视频
    # ----------------------------------------------------------------

    def _step6_images_to_video(self, output_name: str, fps: int) -> str:
        """扫描 Saved/MovieRenders/ 下的 PNG，用 FFmpeg 合成 MP4"""
        movie_capture_dir = _normalize_abs_path(
            os.path.join(unreal.Paths.project_saved_dir(), "MovieRenders")
        )

        print(f"[EffectRecorder] 第六步：图片转视频")
        print(f"[EffectRecorder]   扫描目录: {movie_capture_dir}")

        if not os.path.isdir(movie_capture_dir):
            print("[EffectRecorder]   MovieRenders 目录不存在")
            return None

        # 收集图片
        image_files = []
        for root, _, filenames in os.walk(movie_capture_dir):
            for name in filenames:
                if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
                    image_files.append(_normalize_abs_path(os.path.join(root, name)))

        if not image_files:
            print("[EffectRecorder]   未找到图片文件")
            return None

        print(f"[EffectRecorder]   找到 {len(image_files)} 张图片")
        image_files.sort()

        # 输出视频路径（统一 / 分隔符，供 web 上传使用）
        output_video = _normalize_abs_path(
            os.path.join(movie_capture_dir, f"{output_name}.mp4")
        )
        print(f"[EffectRecorder]   输出视频路径: {output_video}")
        # 重命名为 0000.png 格式（FFmpeg 需要连续数字序列）
        tmp_dir = _normalize_abs_path(os.path.join(movie_capture_dir, "_ffmpeg_temp"))
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)

        for i, src in enumerate(image_files):
            ext = os.path.splitext(src)[1].lower()
            shutil.copy2(src, os.path.join(tmp_dir, f"{i:04d}{ext}"))

        first_ext = os.path.splitext(image_files[0])[1].lower()
        input_pattern = _normalize_abs_path(os.path.join(tmp_dir, f"%04d{first_ext}"))
        cmd = [
            FFMPEG_PATH,
            "-framerate",
            str(fps),
            "-i",
            input_pattern,
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-y",
            output_video,
        ]

        print(f"[EffectRecorder]   FFmpeg 路径: {FFMPEG_PATH}")
        print(f"[EffectRecorder]   执行: {' '.join(cmd)}")

        try:
            run_kwargs = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.PIPE,
                "text": True,
                "timeout": 120,
            }
            if os.name == "nt":
                run_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            result = subprocess.run(cmd, **run_kwargs)
            if result.returncode == 0:
                print(f"[EffectRecorder]   视频生成成功: {output_video}")
                return output_video
            print(f"[EffectRecorder]   FFmpeg 错误: {result.stderr}")
            return None
        except FileNotFoundError:
            print(f"[EffectRecorder]   FFmpeg 未找到: {FFMPEG_PATH}")
            return None
        except subprocess.TimeoutExpired:
            print("[EffectRecorder]   FFmpeg 转换超时")
            return None

    def _cleanup(self):
        self._schedule_cleanup()

    def _schedule_cleanup(self):
        """跨多帧执行清理，避免在同一帧内切关卡/删资产导致崩溃。"""
        _defer_cleanup_chain(
            [
                self._cleanup_close_sequencer,
                self._cleanup_temp_sequence,
                self._cleanup_switch_to_mid_scene,
                self._cleanup_thirdparty_content,
                self._cleanup_movie_render_images,
            ]
        )

    def _cleanup_close_sequencer(self):
        _stop_folder_watch()
        print("[EffectRecorder] 清理临时资产...")

        self._temp_level_actors = []
        self._effect_actor = None
        try:
            unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
            print("[EffectRecorder]   ✓ 已关闭 Sequencer")
        except Exception as e:
            print(f"[EffectRecorder]   关闭 Sequencer 失败: {e}")

    def _cleanup_temp_sequence(self):
        try:
            if unreal.EditorAssetLibrary.does_directory_exist(self._temp_scene_dir):
                unreal.EditorAssetLibrary.delete_directory(self._temp_scene_dir)
                print(f"[EffectRecorder]   ✓ 已删除场景目录: {self._temp_scene_dir}")
        except Exception as e:
            print(f"[EffectRecorder]   删除场景目录失败: {e}")

    def _cleanup_switch_to_mid_scene(self):
        try:
            _ensure_mid_scene_level()
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(
                MID_SCENE_GAME_PATH
            )
            print(f"[EffectRecorder]   已切换到: {MID_SCENE_GAME_PATH}")
        except Exception as e:
            print(f"[EffectRecorder]   切换 midSence 失败: {e}")

    def _cleanup_thirdparty_content(self):
        """删除本次从 ThirdParty 拷贝的具体资产（不删整个 VFX 目录）。"""
        if not self._copied_content_paths:
            return

        print("[EffectRecorder] 清理 ThirdParty 拷贝内容...")
        for game_path in reversed(self._copied_content_paths):
            try:
                _delete_copied_game_path(game_path)
            except Exception as e:
                print(f"[EffectRecorder]   删除失败 {game_path}: {e}")

        self._copied_content_paths = []
        self._needs_cleanup = False

    def _cleanup_movie_render_images(self):
        saved_dir = unreal.Paths.project_saved_dir()
        movie_capture_dir = os.path.join(saved_dir, "MovieRenders")
        try:
            if os.path.isdir(movie_capture_dir):
                for root, _, filenames in os.walk(movie_capture_dir):
                    for name in filenames:
                        if name.lower().endswith((".jpeg", ".jpg", ".png")):
                            os.remove(os.path.join(root, name))
                tmp_dir = os.path.join(movie_capture_dir, "_ffmpeg_temp")
                if os.path.isdir(tmp_dir):
                    shutil.rmtree(tmp_dir)
                print(f"[EffectRecorder]   ✓ 已删除序列图")
        except Exception as e:
            print(f"[EffectRecorder]   删除序列图失败: {e}")

    def _cleanup_assets(self):
        """兼容旧调用，统一走多帧清理。"""
        self._schedule_cleanup()


def upload_effect(asset_list: list):
    """直接调用 BrowserBridge 上传资产，不经过视频录制。"""
    js_call = "web_upload_effect('" + json.dumps(asset_list) + "')"
    print(f"Executing JS: {js_call}")
    unreal.BrowserBridge.open_and_exec_js(js_call)


def record_effect(
    effect_asset,
    asset_list,
    fps: int = DEFAULT_FPS,
    duration_seconds: float = DEFAULT_DURATION_SECONDS,
) -> str:
    global _recorder_instance
    if _recorder_instance is None:
        _recorder_instance = EffectRecorder()
    return _recorder_instance.record(
        effect_asset=effect_asset,
        asset_list=asset_list,
        fps=fps,
        duration_seconds=duration_seconds,
    )
