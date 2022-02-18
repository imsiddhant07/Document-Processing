from bs4 import BeautifulSoup, NavigableString


def parse_authors(parsed_file):
    author_names = parsed_file.find("sourcedesc").findAll("persname")
    authors = []
    for author in author_names:
        firstname = author.find("forename", {"type": "first"})
        firstname = firstname.text.strip() if firstname != None else ""
        middlename = author.find("forename", {"type": "middle"})
        middlename = middlename.text.strip() if middlename != None else ""
        lastname = author.find("surname")
        lastname = lastname.text.strip() if lastname != None else ""
        if middlename != "":
            authors.append(firstname + " " + middlename + " " + lastname)
        else:
            authors.append(firstname + " " + lastname)
    authors = "; ".join(authors)
    return authors


def parse_date(parsed_file):
    pub_date = parsed_file.find("publicationstmt")
    year = pub_date.find("date")
    year = year.attrs.get("when") if year != None else ""
    return year


def parse_abstract(parsed_file):
    """
    Parse abstract from a given BeautifulSoup of an parsed_file
    """
    div = parsed_file.find("abstract")
    abstract = ""
    for p in list(div.children):
        if not isinstance(p, NavigableString) and len(list(p)) > 0:
            abstract += " ".join(
                [elem.text for elem in p if not isinstance(elem, NavigableString)]
            )
    return abstract

def calculate_number_of_references(div):
    """
    For a given section, calculate number of references made in the section
    """
    n_publication_ref = len(
        [ref for ref in div.find_all("ref") if ref.attrs.get("type") == "bibr"]
    )
    n_figure_ref = len(
        [ref for ref in div.find_all("ref") if ref.attrs.get("type") == "figure"]
    )
    return {"n_publication_ref": n_publication_ref, "n_figure_ref": n_figure_ref}


def parse_sections(parsed_file):
    parsed_file_text = parsed_file.find("text")
    divs = parsed_file_text.find_all("div", attrs={"xmlns": "http://www.tei-c.org/ns/1.0"})
    sections = []
    for div in divs:
        div_list = list(div.children)
        if len(div_list) == 0:
            heading = ""
            text = ""
        elif len(div_list) == 1:
            if isinstance(div_list[0], NavigableString):
                heading = str(div_list[0])
                text = ""
            else:
                heading = ""
                text = div_list[0].text
        else:
            text = []
            heading = div_list[0]
            if isinstance(heading, NavigableString):
                heading = str(heading)
                p_all = list(div.children)[1:]
            else:
                heading = ""
                p_all = list(div.children)
            for p in p_all:
                if p != None:
                    try:
                        text.append(p.text)
                    except:
                        pass
            if not False:
                text = "\n".join(text)
        if heading != "" or text != "":
            ref_dict = calculate_number_of_references(div)
            sections.append(
                {
                    "heading": heading,
                    "text": text,
                    "n_publication_ref": ref_dict["n_publication_ref"],
                    "n_figure_ref": ref_dict["n_figure_ref"],
                }
            )
    return sections


def parse_references(parsed_file):
    reference_list = []
    references = parsed_file.find("text").find("div", attrs={"type": "references"})
    references = references.find_all("biblstruct") if references != None else []
    reference_list = []
    for reference in references:
        title = reference.find("title", attrs={"level": "a"})
        if title is None:
            title = reference.find("title", attrs={"level": "m"})
        title = title.text if title != None else ""
        journal = reference.find("title", attrs={"level": "j"})
        journal = journal.text if journal != None else ""
        if journal == "":
            journal = reference.find("publisher")
            journal = journal.text if journal != None else ""
        year = reference.find("date")
        year = year.attrs.get("when") if year != None else ""
        authors = []
        for author in reference.find_all("author"):
            firstname = author.find("forename", {"type": "first"})
            firstname = firstname.text.strip() if firstname != None else ""
            middlename = author.find("forename", {"type": "middle"})
            middlename = middlename.text.strip() if middlename != None else ""
            lastname = author.find("surname")
            lastname = lastname.text.strip() if lastname != None else ""
            if middlename != "":
                authors.append(firstname + " " + middlename + " " + lastname)
            else:
                authors.append(firstname + " " + lastname)
        authors = "; ".join(authors)
        reference_list.append(
            {"title": title, "journal": journal, "year": year, "authors": authors}
        )
    return reference_list


def ref_sentences(article):
    article_text = article.find("text")
    divs = article_text.find_all("div", attrs={"xmlns": "http://www.tei-c.org/ns/1.0"})
    sections = []
    for div in divs:
        for p in div.find_all("p"):
            sentences = p.text.replace("al.", " ").split(".")
            for ref in p.find_all("ref"):
                if ref.attrs.get("type") == "bibr":
                    ref_text = ref.text
                    ref_id = ref.attrs.get("target")
                    ref_sentences = []
                    
                    for sentence in sentences:
                        if ref_text[:7] in sentence and len(ref_sentences)<1:
                            ref_sentences.append(sentence)
                            sentences.remove(sentence)
                    sections.append(
                        {
                            "ref_id": ref_id,
                            "ref_text": ref_text,
                            "ref_sentences": ref_sentences,
                        }
                    )
                
    return sections

    