'''
Run this script to download the model and save it to the model directory. 
Make sure to run this script from the transcript_search directory.
'''

import sentence_transformers

if __name__ == '__main__':
    model = sentence_transformers.SentenceTransformer('multi-qa-mpnet-base-dot-v1')
    model.save('./model')