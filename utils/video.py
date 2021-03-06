import ffmpeg


def generate_thumbnail(in_filename, out_filename, time: float = 0, width: int = 640):
    (
        ffmpeg
            .input(in_filename, ss=time)
            .filter('scale', width, -1)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
    )
