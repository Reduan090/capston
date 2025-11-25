# modules/citation_tool.py
import streamlit as st
from utils.api_helpers import fetch_by_doi, fetch_arxiv
from utils.database import add_reference, get_references
from utils.llm import ask_llm
from config import logger

def main():
    st.header("Citation & Reference Tool")
    query = st.text_input("DOI, arXiv ID, or Query")
    fmt = st.selectbox("Format", ["APA", "MLA", "IEEE", "BibTeX"], key="citation_format_select")
    if st.button("Fetch & Generate"):
        try:
            title, authors, year, doi, bibtex = "", "", "", "", ""
            if "arxiv" in query.lower():
                papers = fetch_arxiv(query)
                if papers:
                    p = papers[0]
                    title = p['title']
                    authors = ", ".join(a['name'] for a in p['authors'])
                    year = p['published'].year
                    doi = p.get('doi', "")
            else:
                work = fetch_by_doi(query)
                if work:
                    title = work['title'][0]
                    authors = ", ".join(a['given'] + " " + a['family'] for a in work.get('author', []))
                    year = work['published']['date-parts'][0][0]
                    doi = work['DOI']

            if title:
                prompt = f"Generate {fmt} citation: Title: {title}, Authors: {authors}, Year: {year}, DOI: {doi}"
                citation = ask_llm(prompt)
                if fmt == "BibTeX":
                    bibtex = citation
                add_reference(title, authors, str(year), doi, bibtex)
                st.write(citation)
            else:
                st.warning("No data found.")
        except Exception as e:
            st.error(str(e))
            logger.error(str(e))

    st.subheader("Stored References")
    refs = get_references()
    for ref in refs:
        st.write(f"{ref[1]} ({ref[3]}) - {ref[2]}")