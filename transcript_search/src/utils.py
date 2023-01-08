from PIL import Image
import numpy as np
import base64
from io import BytesIO

def create_transcript_chunks(transcript, stride=1, length=2):
    '''Create larger chunks of the segments using a sliding window'''

    all_start_times = [segment['time'] for segment in transcript]

    transcript_chunks = []
    for i in range(0, len(all_start_times), stride):
        chunk = {}
        chunk['start'] = all_start_times[i]
        chunk['text'] = "".join([segment['text'] for segment in transcript[i:i+length]]).strip()

        transcript_chunks.append(chunk)

    return transcript_chunks

def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"

def convert_base64_to_image(image_str, return_type='pillow'):
    '''
    Converts a base64 encoded image to Pillow Image or Numpy Array

    Args:
        image_str (str): The pure base64 encoded string of the image
        return_type (str): The type of image you want to convert it to. 
                           Choices are [ numpy | pillow ]. Default is pillow.
    Returns:
        PIL.Image or numpy.array: The converted image
    '''
    image = Image.open(BytesIO(base64.b64decode(image_str))).convert('RGB')
    if return_type == 'numpy':
        return np.array(image)
    else:
        return image