from bs4 import BeautifulSoup
from parse import parse_authors
from parse import parse_references
from parse import parse_sections
from parse import parse_abstract
from parse import parse_date
from parse import ref_sentences
from similarity import lexicalScore
from similarity import semanticScore
import pandas as pd
from grobid_client.grobid_client import GrobidClient

if __name__ == "__main__":
    client = GrobidClient(config_path="./config.json")
    client.process("processFulltextDocument", "./data/input", output="./data/output/xml", consolidate_citations=True, force=True)

    parsed_file = BeautifulSoup(open("/home/siddhant/Projects/have-a-look-at-my-paper/data/output/xml/P19-1106.tei.xml"), "lxml")

    # ------------------------------------------- 

    sections = parse_sections(parsed_file)
    heads = []
    content = []
    for section in sections:
        heads.append(section['heading'])
        content.append(section['text'])

    paper_sections = pd.DataFrame()
    paper_sections['heading'] = heads
    paper_sections['content'] = content

    paper_sections.to_csv("/home/siddhant/Projects/have-a-look-at-my-paper/data/output/csv/sections.csv", index=False)


    # -------------------------------------------

    citations = parse_references(parsed_file)
    titles = []
    journals = []
    authors = []
    for cit in citations:
        titles.append(cit['title'])
        journals.append(cit['journal'])
        authors.append(cit['authors'])

    citations_data = pd.DataFrame()
    citations_data['title'] = titles
    citations_data['journal'] = journals
    citations_data['authors'] = authors

    citations_data.to_csv("/home/siddhant/Projects/have-a-look-at-my-paper/data/output/csv/citations.csv", index=False)


    # -------------------------------------------

    ref_sentence  = []
    ref_citation = []
    ref_venue = []

    sentences = ref_sentences(parsed_file)
    for sentence in sentences:
        if sentence['ref_id'] is not None:
            sentence['ref_id'] = int(sentence['ref_id'].replace('#b', ''))


    for i in range(len(sentences)):
        ref_sentence.append(sentences[i]['ref_sentences'][0])
        if sentences[i]['ref_id'] is not None:
            index = sentences[i]['ref_id']
            ref_citation.append(citations[index]['title'])
        else:
            ref_citation.append(None)
        ref_venue.append(citations[index]['journal'])
            
    ref_sentence_data = pd.DataFrame()
    ref_sentence_data['ref sentence'] = ref_sentence
    ref_sentence_data['ref citation'] = ref_citation
    ref_sentence_data['ref venue'] = ref_venue

    ref_sentence_data.to_csv("/home/siddhant/Projects/have-a-look-at-my-paper/data/output/csv/ref_sentences.csv", index=False)

    # ----------------------------------------

    ref_semantic = []
    ref_lexical = []

    for i in range(len(ref_sentence)):
        if ref_citation[i] is not None:
            ref_semantic.append(semanticScore(ref_sentence[i], ref_citation[i]))
            ref_lexical.append(lexicalScore(ref_sentence[i], ref_citation[i]))
        else:
            ref_semantic.append(None)
            ref_lexical.append(None)

    similarity = pd.DataFrame()
    similarity['ref sentence'] = ref_sentence
    similarity['ref citation'] = ref_citation
    similarity['semantic score'] = ref_semantic
    similarity['lexical score'] = ref_lexical

    similarity.to_csv("/home/siddhant/Projects/have-a-look-at-my-paper/data/output/csv/similarity.csv", index=False)