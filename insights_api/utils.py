import re

def postprocess_points(raw_output):
    raw_output = re.sub(r'\n\s*-', '\n-', raw_output)
    points = raw_output.split('\n-')
    points = [point.strip() for point in points]
    points = [point for point in points if point != '']
    return points
    
def format_transcript_str(transcript):
    
    transcript_str = []
    for segment in transcript:
        transcript_str.append(f"[{segment['timestamp']}]:\t{segment['text']}")
    
    transcript_str = "\n".join(transcript_str)
    return transcript_str