"""
動画ファイル一括MP4変換ヘルパースクリプト (helper/convert_video.py)

指定したディレクトリ（デフォルト: assets/vid/）内の動画ファイル (.mov, .avi, .mkv 等) を
Pygame等で再生互換性の高い .mp4 (H.264 / AAC) 形式に自動一括変換します。
"""

import os
import sys
import argparse
import subprocess

try:
    import imageio_ffmpeg
except ImportError:
    print("エラー: imageio-ffmpeg パッケージが見つかりません。")
    print("実行前に `pip install imageio-ffmpeg` を実行してください。")
    sys.exit(1)


def convert_video_to_mp4(input_path: str, output_path: str, overwrite: bool = False) -> bool:
    """単一の動画ファイルを .mp4 に変換"""
    if os.path.exists(output_path) and not overwrite:
        print(f"スキップ (既に存在します): {output_path}")
        return True

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-y" if overwrite else "-n",
        "-i", input_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        output_path
    ]

    print(f"変換中: {input_path} -> {output_path}")
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print(f"✅ 変換成功: {output_path}")
            return True
        else:
            print(f"❌ 変換失敗: {input_path}\n{res.stderr}")
            return False
    except Exception as e:
        print(f"エラー発生: {e}")
        return False


def process_directory(target_dir: str, overwrite: bool = False):
    """指定ディレクトリ内の全動画を一括変換"""
    if not os.path.exists(target_dir):
        print(f"指定されたディレクトリが存在しません: {target_dir}")
        return

    valid_extensions = {".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"}
    converted_count = 0

    for root, _, files in os.walk(target_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions:
                input_file = os.path.join(root, file)
                output_file = os.path.splitext(input_file)[0] + ".mp4"
                
                # 自分自身が mp4 の場合はスキップ
                if input_file.lower() == output_file.lower():
                    continue

                if convert_video_to_mp4(input_file, output_file, overwrite=overwrite):
                    converted_count += 1

    print(f"\n処理完了: 計 {converted_count} 件の動画を処理しました。")


def main():
    parser = argparse.ArgumentParser(description="MOV/AVI等の動画ファイルをMP4に一括変換するツール")
    parser.add_argument("--dir", "-d", default="assets/vid", help="対象動画ディレクトリ (デフォルト: assets/vid)")
    parser.add_argument("--file", "-f", default=None, help="単一ファイルを指定する場合")
    parser.add_argument("--overwrite", "-w", action="store_true", help="既存の.mp4ファイルを強制上書きする")

    args = parser.parse_args()

    if args.file:
        if not os.path.exists(args.file):
            print(f"ファイルが見つかりません: {args.file}")
            sys.exit(1)
        out_file = os.path.splitext(args.file)[0] + ".mp4"
        convert_video_to_mp4(args.file, out_file, overwrite=args.overwrite)
    else:
        process_directory(args.dir, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
