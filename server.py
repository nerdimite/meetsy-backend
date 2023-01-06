import json
import os
import base64

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import numpy as np
import moviepy.editor as mp
from inference import LISAPipeline
from random_uid import generate_random_uid


class VideoInput(BaseModel):
    video: str

class SearchQuery(BaseModel):
    job_id: str
    query: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
)

@app.on_event("startup")
async def startup_event():
    global lisa
    lisa = LISAPipeline(whisper_model="whisper_models/medium.pt", search_model="multi-qa-mpnet-base-dot-v1")

@app.post("/predict")
async def predict(payload: VideoInput):

    print('Received Video Payload')

    # create uid
    while True:
        job_id = generate_random_uid()
        job_dir = f"results/{job_id}"
        if not os.path.exists(job_dir):
            os.makedirs(job_dir, exist_ok=True)
            break

    # save video
    with open(os.path.join(job_dir, "meeting.mp4"), "wb") as f:
        video_bytes = base64.decodebytes(payload.video.split(",")[1].encode('utf-8'))
        f.write(video_bytes)

    # convert video to audio
    video = mp.VideoFileClip(os.path.join(job_dir, "meeting.mp4"))
    audio_path = os.path.join(job_dir, "meeting.mp3")
    video.audio.write_audiofile(audio_path)

    # run inference
    minutes, action_items, doc_emb, transcript_chunks, transcript = lisa(audio_path)
    results = {
        "job_id": job_id,
        "minutes": minutes,
        "action_items": action_items,
        "doc_emb": doc_emb.tolist(),
        "transcript_chunks": transcript_chunks,
        "transcription": transcript
    }

    # save results
    with open(os.path.join(job_dir, "results.json"), "w") as f:
        json.dump(results, f)

    # job_id = 'amiable-mother-256'
    # job_dir = 'results/amiable-mother-256'

    # with open(os.path.join(job_dir, "results.json"), "r") as f:
    #     results = json.load(f)

    output = {
        "job_id": job_id,
        "minutes": results['minutes'],
        "action_items": results['action_items'],
        "transcription": results['transcription']
    }
    print(output)

    return output

@app.get("/results/{job_id}")
async def fetch_results(job_id: str):

    # load results
    with open(os.path.join("results", job_id, "results.json"), "r") as f:
        results = json.load(f)

    return results

@app.post("/search")
async def search(search_query: SearchQuery):

    job_id = search_query.job_id
    query = search_query.query
    
    # load job results
    with open(os.path.join("results", job_id, "results.json"), "r") as f:
        results = json.load(f)

    # search
    doc_emb = np.array(results["doc_emb"], dtype=np.float32)
    transcript_chunks = results['transcript_chunks']
    search_results = lisa.search(doc_emb, transcript_chunks, query)
    print(search_results)

    return search_results

