import os
import subprocess
from pathlib import Path

def compress_video(input_file: str, output_file: str, crf: int = 28):
    """使用 FFmpeg 压缩单个视频"""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-vcodec", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", str(crf),
        "-preset", "slow",
        "-an",           # 移除音频
        output_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return result.returncode, result.stderr.decode()


def compress_all_videos(video_dir: str, crf: int = 28):
    """
    压缩指定目录及子目录下的所有视频，压缩完成后替换原文件
    """
    video_dir = Path(video_dir)
    video_files = list(video_dir.rglob("*.mp4"))

    if not video_files:
        print(f"未找到任何视频文件: {video_dir}")
        return

    print(f"共找到 {len(video_files)} 个视频文件，开始压缩...\n")

    # 统计压缩前总大小
    total_before = sum(f.stat().st_size for f in video_files)

    success_count = 0
    fail_count = 0

    for i, video_file in enumerate(video_files, 1):
        size_before = video_file.stat().st_size / (1024 * 1024)  # MB
        tmp_file = video_file.with_stem(video_file.stem + "_tmp_compressed")

        print(f"[{i}/{len(video_files)}] 压缩: {video_file.relative_to(video_dir)}")
        print(f"  压缩前大小: {size_before:.2f} MB")

        returncode, stderr = compress_video(str(video_file), str(tmp_file), crf)

        if returncode != 0:
            print(f"  ✗ 压缩失败: {stderr}")
            if tmp_file.exists():
                tmp_file.unlink()
            fail_count += 1
            continue

        size_after = tmp_file.stat().st_size / (1024 * 1024)  # MB
        ratio = (1 - size_after / size_before) * 100
        print(f"  压缩后大小: {size_after:.2f} MB  (压缩率: {ratio:.1f}%)")

        # 替换原文件（保持文件名不变）
        tmp_file.replace(video_file)
        print(f"  ✓ 已替换原文件: {video_file.name}\n")
        success_count += 1

    # 统计压缩后总大小
    total_after = sum(f.stat().st_size for f in video_files)
    total_before_mb = total_before / (1024 * 1024)
    total_after_mb  = total_after  / (1024 * 1024)
    total_ratio = (1 - total_after / total_before) * 100

    print("=" * 50)
    print(f"压缩完成！成功: {success_count} 个，失败: {fail_count} 个")
    print(f"压缩前总大小: {total_before_mb:.2f} MB")
    print(f"压缩后总大小: {total_after_mb:.2f} MB")
    print(f"总压缩率: {total_ratio:.1f}%")
    print("=" * 50)


if __name__ == "__main__":
    VIDEO_DIR = "input_path"
    CRF = 28   # 画质：18~28（越大压缩率越高，建议网页用 26~30）

    # 备份（可选，推荐执行）
    import shutil
    backup_dir = "temp"
    if not Path(backup_dir).exists():
        print("正在备份原始视频...")
        shutil.copytree(VIDEO_DIR, backup_dir)
        print(f"备份完成: {backup_dir}\n")

    compress_all_videos(VIDEO_DIR, CRF)