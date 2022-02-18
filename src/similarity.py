import spacy 
nlp = spacy.load('en_core_web_md')

def lexicalScore(sentence1, sentence2):
    # List the unique words in a document
    words_sentence1 = set(sentence1.lower().split()) 
    words_sentence2 = set(sentence2.lower().split())
    
    # Find the intersection of words list of sentence1 & sentence2
    intersection = words_sentence1.intersection(words_sentence2)

    # Find the union of words list of sentence1 & sentence2
    union = words_sentence1.union(words_sentence2)
        
    # Calculate Jaccard similarity score 
    # using length of intersection set divided by length of union set
    return float(len(intersection)) / len(union)

def semanticScore(sentence1, sentence2):
    # Tokenize the sentences
    doc1 = nlp(sentence1)
    doc2 = nlp(sentence2)
    
    # Find the similarity score using the cosine similarity function
    return doc1.similarity(doc2)

