import os
from hub import hub_handler
from sentence_transformers import SentenceTransformer, util
from utils import create_transcript_chunks, format_timestamp

MODEL_DIR = os.getenv("MODEL_DIR")

print('Loading Sentence Transformer...')
search_model = SentenceTransformer.load(MODEL_DIR)

def create_index(transcript):
    '''Create search index by embedding the transcript segments'''

    transcript_chunks = create_transcript_chunks(transcript)

    # Encode query and documents
    chunk_texts = [chunk['text'] for chunk in transcript_chunks]
    doc_emb = search_model.encode(chunk_texts)

    return doc_emb, transcript_chunks

def search(doc_embeddings, transcript_chunks, query, top_k=3):
    # Compute dot score between query and all document embeddings
    query_embeddings = search_model.encode(query)
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

    return results

@hub_handler
def inference_handler(inputs, _):
    '''The main inference function which gets triggered when the API is invoked'''
    
    transcript, query = inputs['transcript'], inputs['query']
    
    doc_emb, transcript_chunks = create_index(transcript)
    search_results = search(doc_emb, transcript_chunks, query)
    print(search_results)

    return search_results
