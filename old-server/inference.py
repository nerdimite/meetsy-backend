import openai
import whisper
from sentence_transformers import SentenceTransformer, util
from utils import create_transcript_chunks, create_transcript, postprocess_points, format_timestamp

openai.api_key = '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' # os.getenv("OPENAI_API_KEY")

class LISAPipeline():
    def __init__(self, whisper_model, search_model):
        print('Loading Whisper...')
        self.whisper_model = whisper.load_model(whisper_model)
        print('Loading Sentence Transformer...')
        self.search_model = SentenceTransformer.load(search_model)
        print('Models loaded!')
    
    def run_gpt3(self, prompt, max_tokens=256, temperature=0.5, top_p=1, frequency_penalty=0.0, presence_penalty=0.0):
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        return response.choices[0].text
    
    def transcribe(self, audio_path):
        whisper_out = self.whisper_model.transcribe(audio_path, verbose=False)
        return whisper_out
    
    def minutes_of_meeting(self, transcript_str):

        mom_prompt = f"""Generate a meeting summary/notes for the following transcript:
        Meeting Transcription:
        {transcript_str}

        Instructions:
        1. Do not use the same words as in the transcript.
        2. Use proper grammar and punctuation.
        3. Use bullets to list the points.
        4. Add as much detail as possible.

        Meeting Minutes:
        -"""

        raw_minutes = self.run_gpt3(mom_prompt, temperature=0.5)
        minutes = postprocess_points(raw_minutes)

        return minutes

    def action_items(self, transcript_str):

        action_prompt = f"""Extract the Action Items / To-Do List from the Transcript.
        Meeting Transcription:
        {transcript_str}

        Action Items:
        -"""
        raw_action_items = self.run_gpt3(action_prompt, temperature=0.4)
        action_items = postprocess_points(raw_action_items)

        return action_items

    def create_index(self, transcript):
        '''Create search index by embedding the transcript segments'''

        transcript_chunks = create_transcript_chunks(transcript)

        # Encode query and documents
        chunk_texts = [chunk['text'] for chunk in transcript_chunks]
        doc_emb = self.search_model.encode(chunk_texts)

        return doc_emb, transcript_chunks
    
    def search(self, doc_embeddings, transcript_chunks, query, top_k=3, threshold=14):
        # Compute dot score between query and all document embeddings
        query_embeddings = self.search_model.encode(query)
        scores = util.dot_score(query_embeddings, doc_embeddings)[0].cpu().tolist()

        chunks = [(chunk['start'], chunk['text']) for chunk in transcript_chunks]

        # Combine docs & scores
        chunk_score_tuples = [(*chunks[i], scores[i]) for i in range(len(chunks))]

        # Sort by decreasing score
        chunk_score_tuples = sorted(chunk_score_tuples, key=lambda x: x[-1], reverse=True)

        # Output passages & scores
        results = []
        for start, text, score in chunk_score_tuples[:top_k]:
            results.append({
                'time': start,
                'timestamp': format_timestamp(start),
                'text': text,
                'confidence': score
            })
            # if score > threshold:
            #     results.append((start, end, text))
            # print('Score', score, text)

        return results

    def __call__(self, audio_path):
        '''Run the pipeline on an audio file'''
        whisper_out = self.transcribe(audio_path)
        transcript_str, transcript = create_transcript(whisper_out)
        minutes = self.minutes_of_meeting(transcript_str)
        action_items = self.action_items(transcript_str)
        doc_emb, transcript_chunks = self.create_index(transcript)

        return minutes, action_items, doc_emb, transcript_chunks, transcript