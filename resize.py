import os
import cv2
import subprocess
from pathlib import Path

def resize_videos(input_dir: str, output_dir: str, width: int, height: int):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}

    video_files = [
        f for f in input_path.rglob('*')
        if f.suffix.lower() in video_extensions
    ]

    if not video_files:
        print(f"未找到任何视频文件: {input_dir}")
        return

    print(f"共找到 {len(video_files)} 个视频文件，开始处理...")

    for i, video_file in enumerate(video_files, 1):
        relative_path = video_file.relative_to(input_path)
        output_file = output_path / relative_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # cv2 先输出临时文件
        tmp_file = output_file.with_stem(output_file.stem + "_tmp")

        print(f"[{i}/{len(video_files)}] 处理: {video_file.name}")

        try:
            # ── Step 1: cv2 resize ──────────────────────────────────────
            cap = cv2.VideoCapture(str(video_file))
            fps = cap.get(cv2.CAP_PROP_FPS)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(tmp_file), fourcc, fps, (width, height))

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                resized_frame = cv2.resize(frame, (width, height))
                out.write(resized_frame)

            cap.release()
            out.release()

            # ── Step 2: FFmpeg 转换为 H.264 + yuv420p ──────────────────
            cmd = [
                "ffmpeg", "-y",
                "-i", str(tmp_file),
                "-vcodec", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "23",           # 画质，越小越好，建议 18~28
                "-preset", "fast",      # 编码速度
                str(output_file)
            ]
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

            if result.returncode != 0:
                print(f"  ✗ FFmpeg 转换失败: {result.stderr.decode()}")
            else:
                print(f"  ✓ 已保存到: {output_file}")

        except Exception as e:
            print(f"  ✗ 处理失败: {e}")

        finally:
            # 删除临时文件
            if tmp_file.exists():
                tmp_file.unlink()

    print("\n全部处理完成！")


if __name__ == "__main__":
    INPUT_DIR  = "input_path"
    OUTPUT_DIR = "output_path"
    WIDTH  = 640
    HEIGHT = 360

    resize_videos(INPUT_DIR, OUTPUT_DIR, WIDTH, HEIGHT)