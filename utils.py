import re
from words import ADJECTIVES, POLITE_ADJECTIVES, NOUNS, ANIMALS

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

def create_transcript(whisper_out):
        
    transcript_str = []
    transcript = []
    for segment in whisper_out['segments']:
        transcript_str.append(f"[{format_timestamp(segment['start'])}]:\t{segment['text']}")
        transcript.append(
            {
                'time': segment['start'],
                'timestamp': format_timestamp(segment['start']),
                'text': segment['text']
            }
        )
    
    transcript_str = "\n".join(transcript_str)
    return transcript_str, transcript

def postprocess_points(raw_output):
    raw_output = re.sub(r'\n\s*-', '\n-', raw_output)
    points = raw_output.split('\n-')
    points = [point.strip() for point in points]
    points = [point for point in points if point != '']
    return points

def find_closest_time(time, all_times):
    closest_time = min(all_times, key=lambda x: abs(x - time))
    return closest_time

def create_transcript_chunks(transcript, stride=3, length=3):
    '''Create larger chunks of the segments using a sliding window'''

    all_start_times = [segment['time'] for segment in transcript]

    transcript_chunks = []
    for i in range(0, len(all_start_times), stride):
        chunk = {}
        chunk['start'] = all_start_times[i]
        chunk['text'] = "".join([segment['text'] for segment in transcript[i:i+length]]).strip()

        transcript_chunks.append(chunk)

    # for seek in range(0, int(all_end_times[-1]), stride):
    #     chunk = {'start': None, 'end': None, 'text': None}

    #     start_index = all_start_times.index(find_closest_time(seek, all_start_times))
    #     chunk['start'] = all_start_times[start_index]
    #     end_index = all_end_times.index(find_closest_time(seek + length, all_end_times))
    #     chunk['end'] = all_end_times[end_index]

    #     chunk['text'] = "".join([segment['text'] for segment in whisper_out['segments'][start_index:end_index+1]]).strip()

    #     transcript_chunks.append(chunk)
    
    return transcript_chunks