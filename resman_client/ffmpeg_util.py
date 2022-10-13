import logging
import subprocess
from itertools import chain

log = logging.getLogger(__file__)


def get_video_codec(video_file: str) -> str:
    return subprocess.check_output(
        [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_file
        ]
    ).decode().strip()


def get_audio_codec(video_file: str) -> str:
    return subprocess.check_output(
        [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_file
        ]
    ).decode().strip()


def convert_file_codec_qsv(input_file: str, output_file: str, transcode_audio: bool):
    return subprocess.check_call(list(chain(
        ["ffmpeg", "-y", "-i", input_file],
        "-init_hw_device qsv=hw -filter_hw_device hw -vf "
        "hwupload=extra_hw_frames=64,scale_qsv=format=nv12 -c:v h264_qsv "
        "-maxrate 5M -movflags +faststart -q:v 25".split(" "),
        ("-c:a aac -q:a 2" if transcode_audio else "-c:a copy").split(" "),
        [output_file]
    )))


def convert_file_codec(input_file: str, output_file: str, transcode_audio: bool):
    return subprocess.check_call(list(chain(
        ["ffmpeg", "-y", "-i", input_file],
        "-c:v h264 -movflags +faststart -pix_fmt yuv420p -crf 23".split(" "),
        ("-c:a aac -q:a 2" if transcode_audio else "-c:a copy").split(" "),
        [output_file]
    )))


def copy_codec(input_file: str, output_file: str, transcode_audio: bool):
    return subprocess.check_call(list(chain(
        ["ffmpeg", "-y", "-i", input_file],
        "-c:v copy".split(" "),
        ("-c:a aac -q:a 2" if transcode_audio else "-c:a copy").split(" "),
        [output_file]
    )))


def is_h264_qsv_available():
    return any(
        s.find("h264_qsv") >= 0
        for s in subprocess.check_output("ffmpeg -encoders -v error".split(" ")).decode().split("\n")
    )


def convert_video_to_h264(input_file: str, output_file: str, use_qsv: bool = False, force_convert: bool = False):
    """
    Convert video to H264 format
    :param input_file: input file
    :param output_file: output file
    :param use_qsv: try QSV if ffmpeg support it
    :param force_convert: ignore source format and re-encode the file
    :return:
    """
    if get_video_codec(input_file) != "h264" or force_convert:
        h264_qsv_available = is_h264_qsv_available()
        if h264_qsv_available:
            log.info(f"QSV is available! use_qsv={use_qsv}")
        func = convert_file_codec_qsv if h264_qsv_available and use_qsv else convert_file_codec
    else:
        func = copy_codec
    return func(input_file, output_file, get_audio_codec(input_file) != "aac")
