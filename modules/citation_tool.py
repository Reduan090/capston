# modules/citation_tool.py
import streamlit as st
from utils.api_helpers import fetch_by_doi, fetch_arxiv, fetch_papers
from utils.database import add_reference, get_references
from utils.llm import ask_llm
from config import logger, EXPORT_DIR
import json

def generate_citation(citation_data, format_type):
    """Generate citation in specified format with high accuracy"""
    
    title = citation_data.get('title', '')
    authors = citation_data.get('authors', [])
    year = citation_data.get('year', '')
    journal = citation_data.get('journal', '')
    volume = citation_data.get('volume', '')
    issue = citation_data.get('issue', '')
    pages = citation_data.get('pages', '')
    doi = citation_data.get('doi', '')
    url = citation_data.get('url', '')
    publisher = citation_data.get('publisher', '')
    edition = citation_data.get('edition', '')
    
    # Author formatting
    if isinstance(authors, list):
        author_str = ", ".join(authors)
    else:
        author_str = authors
    
    # Format-specific templates
    if format_type == "APA 7th":
        # APA 7th Edition
        citation = f"{author_str} ({year}). {title}."
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f", *{volume}*"
            if issue:
                citation += f"({issue})"
            if pages:
                citation += f", {pages}"
        if doi:
            citation += f". https://doi.org/{doi}"
        elif url:
            citation += f". {url}"
        return citation
    
    elif format_type == "MLA 9th":
        # MLA 9th Edition
        citation = f"{author_str}. \"{title}.\""
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f", vol. {volume}"
            if issue:
                citation += f", no. {issue}"
            if year:
                citation += f", {year}"
            if pages:
                citation += f", pp. {pages}"
        if doi:
            citation += f", doi:{doi}"
        return citation + "."
    
    elif format_type == "IEEE":
        # IEEE Style
        citation = f"{author_str}, \"{title},\""
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f", vol. {volume}"
            if issue:
                citation += f", no. {issue}"
            if pages:
                citation += f", pp. {pages}"
            if year:
                citation += f", {year}"
        if doi:
            citation += f", doi: {doi}"
        return citation + "."
    
    elif format_type == "Chicago":
        # Chicago Style
        citation = f"{author_str}. {year}. \"{title}.\""
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f" {volume}"
            if issue:
                citation += f" ({issue})"
            if pages:
                citation += f": {pages}"
        if doi:
            citation += f". https://doi.org/{doi}"
        return citation + "."
    
    elif format_type == "Springer":
        # Springer/Nature Style
        citation = f"{author_str} ({year}) {title}."
        if journal:
            citation += f" {journal}"
            if volume:
                citation += f" {volume}"
            if pages:
                citation += f":{pages}"
        if doi:
            citation += f". https://doi.org/{doi}"
        return citation
    
    elif format_type == "Harvard":
        # Harvard Style
        citation = f"{author_str}, {year}. {title}."
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f", {volume}"
            if issue:
                citation += f"({issue})"
            if pages:
                citation += f", pp.{pages}"
        if doi:
            citation += f". DOI: {doi}"
        return citation + "."
    
    elif format_type == "Vancouver":
        # Vancouver Style
        citation = f"{author_str}. {title}."
        if journal:
            citation += f" {journal}."
            if year:
                citation += f" {year}"
            if volume:
                citation += f";{volume}"
            if issue:
                citation += f"({issue})"
            if pages:
                citation += f":{pages}"
        if doi:
            citation += f". doi:{doi}"
        return citation + "."
    
    elif format_type == "BibTeX":
        # BibTeX format
        # Clean title for BibTeX key
        key = title[:20].replace(" ", "_").replace(",", "").replace(":", "") + year
        
        bibtex = f"""@article{{{key},
  author = {{{author_str}}},
  title = {{{title}}},
  year = {{{year}}}"""
        
        if journal:
            bibtex += f",\n  journal = {{{journal}}}"
        if volume:
            bibtex += f",\n  volume = {{{volume}}}"
        if issue:
            bibtex += f",\n  number = {{{issue}}}"
        if pages:
            bibtex += f",\n  pages = {{{pages}}}"
        if doi:
            bibtex += f",\n  doi = {{{doi}}}"
        
        bibtex += "\n}"
        return bibtex
    
    # Fallback - use LLM
    prompt = f"""Generate a properly formatted {format_type} citation:

Title: {title}
Authors: {author_str}
Year: {year}
Journal: {journal}
Volume: {volume}
Issue: {issue}
Pages: {pages}
DOI: {doi}
URL: {url}
Publisher: {publisher}

Generate only the citation, nothing else."""
    
    return ask_llm(prompt, temperature=0.1)

def manual_citation_entry():
    """Allow manual entry of citation details"""
    st.write("### 📝 Manual Citation Entry")
    st.write("Enter publication details to generate citations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Title*", key="manual_title")
        authors = st.text_input("Authors* (comma-separated)", key="manual_authors", 
                               placeholder="Smith, J., Doe, A.")
        year = st.text_input("Year*", key="manual_year", placeholder="2024")
        
    with col2:
        publication_type = st.selectbox(
            "Publication Type",
            ["Journal Article", "Book", "Conference Paper", "Thesis", "Web Page"],
            key="pub_type"
        )
        journal = st.text_input("Journal/Conference Name", key="manual_journal")
        publisher = st.text_input("Publisher", key="manual_publisher")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        volume = st.text_input("Volume", key="manual_volume")
    with col4:
        issue = st.text_input("Issue", key="manual_issue")
    with col5:
        pages = st.text_input("Pages", key="manual_pages", placeholder="123-456")
    
    col6, col7 = st.columns(2)
    with col6:
        doi = st.text_input("DOI", key="manual_doi", placeholder="10.1234/example")
    with col7:
        url = st.text_input("URL", key="manual_url")
    
    # Format selection
    formats = ["APA 7th", "MLA 9th", "IEEE", "Chicago", "Springer", "Harvard", "Vancouver", "BibTeX"]
    selected_formats = st.multiselect(
        "Select Citation Formats (you can select multiple)",
        formats,
        default=["APA 7th", "IEEE", "BibTeX"]
    )
    
    if st.button("📋 Generate Citations", key="gen_manual"):
        if not title or not authors or not year:
            st.warning("Please fill in at least Title, Authors, and Year.")
            return
        
        citation_data = {
            'title': title,
            'authors': [a.strip() for a in authors.split(',')],
            'year': year,
            'journal': journal,
            'volume': volume,
            'issue': issue,
            'pages': pages,
            'doi': doi,
            'url': url,
            'publisher': publisher
        }
        
        st.write("### 📚 Generated Citations:")
        
        for fmt in selected_formats:
            with st.expander(f"**{fmt} Format**", expanded=True):
                try:
                    citation = generate_citation(citation_data, fmt)
                    st.code(citation, language=None)
                    
                    # Copy button simulation
                    if st.button(f"Copy {fmt}", key=f"copy_{fmt}"):
                        st.info("Citation displayed above - use browser copy function")
                except Exception as e:
                    st.error(f"Error generating {fmt}: {str(e)}")
        
        # Save to database
        if st.button("💾 Save to Library"):
            try:
                bibtex = generate_citation(citation_data, "BibTeX")
                add_reference(title, ", ".join(citation_data['authors']), year, doi, bibtex)
                st.success("✅ Saved to citation library!")
            except Exception as e:
                st.error(f"Error saving: {str(e)}")

def auto_fetch_citation():
    """Automatically fetch citation from DOI or other identifiers"""
    st.write("### 🔍 Auto-Fetch Citation")
    st.write("Enter a DOI, arXiv ID, or search query to automatically fetch citation details.")
    
    query = st.text_input(
        "Enter DOI, arXiv ID, or search query",
        placeholder="e.g., 10.1038/nature12373 or arXiv:2103.00020",
        key="auto_query"
    )
    
    if st.button("🔍 Fetch Citation Data", key="fetch_btn"):
        if not query:
            st.warning("Please enter a DOI, arXiv ID, or query.")
            return
        
        with st.spinner("Fetching citation data..."):
            try:
                citation_data = None
                
                # Try arXiv
                if "arxiv" in query.lower():
                    papers = fetch_arxiv(query)
                    if papers:
                        p = papers[0]
                        citation_data = {
                            'title': p.get('title', ''),
                            'authors': [a['name'] for a in p.get('authors', [])],
                            'year': str(p['published'].year) if 'published' in p else '',
                            'journal': 'arXiv',
                            'doi': p.get('doi', ''),
                            'url': p.get('pdf_url', '')
                        }
                
                # Try DOI
                elif query.startswith('10.'):
                    work = fetch_by_doi(query)
                    if work:
                        authors = []
                        for a in work.get('author', []):
                            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                            if name:
                                authors.append(name)
                        
                        citation_data = {
                            'title': work.get('title', [''])[0],
                            'authors': authors,
                            'year': str(work.get('published', {}).get('date-parts', [['']])[0][0]),
                            'journal': work.get('container-title', [''])[0] if work.get('container-title') else '',
                            'volume': str(work.get('volume', '')),
                            'issue': str(work.get('issue', '')),
                            'pages': work.get('page', ''),
                            'doi': work.get('DOI', ''),
                            'publisher': work.get('publisher', '')
                        }
                
                # Try search
                else:
                    papers = fetch_papers(query, limit=1)
                    if papers:
                        p = papers[0]
                        citation_data = {
                            'title': p.get('title', ''),
                            'authors': [a.get('name', '') for a in p.get('authors', [])],
                            'year': str(p.get('year', '')),
                            'journal': p.get('venue', ''),
                            'doi': p.get('externalIds', {}).get('DOI', '') if 'externalIds' in p else ''
                        }
                
                if citation_data:
                    st.success("✅ Citation data fetched successfully!")
                    
                    # Display the data
                    st.write("#### Retrieved Information:")
                    st.json(citation_data)
                    
                    # Generate in all formats
                    st.write("#### Generated Citations:")
                    formats = ["APA 7th", "MLA 9th", "IEEE", "Chicago", "Springer", "Harvard", "Vancouver", "BibTeX"]
                    
                    for fmt in formats:
                        with st.expander(f"**{fmt} Format**"):
                            try:
                                citation = generate_citation(citation_data, fmt)
                                st.code(citation, language=None)
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    # Save option
                    if st.button("💾 Save to Library", key="save_auto"):
                        try:
                            bibtex = generate_citation(citation_data, "BibTeX")
                            add_reference(
                                citation_data['title'],
                                ", ".join(citation_data['authors']),
                                citation_data['year'],
                                citation_data.get('doi', ''),
                                bibtex
                            )
                            st.success("✅ Saved to citation library!")
                        except Exception as e:
                            st.error(f"Error saving: {str(e)}")
                else:
                    st.warning("No citation data found. Try manual entry.")
                    
            except Exception as e:
                st.error(f"Error fetching citation: {str(e)}")
                logger.error(f"Auto-fetch error: {e}")

def citation_library():
    """Manage stored citations"""
    st.write("### 📚 Citation Library")
    st.write("View and manage your saved citations.")
    
    try:
        refs = get_references()
        
        if not refs:
            st.info("No citations saved yet. Add citations using the tools above.")
            return
        
        st.write(f"**Total Citations:** {len(refs)}")
        
        # Export all option
        col1, col2 = st.columns([3, 1])
        with col2:
            export_format = st.selectbox("Export Format", ["BibTeX", "JSON", "Plain Text"])
            if st.button("📥 Export All"):
                try:
                    export_file = EXPORT_DIR / f"citations_export.{export_format.lower().replace(' ', '_')}"
                    
                    if export_format == "BibTeX":
                        content = "\n\n".join([ref[5] for ref in refs if ref[5]])  # BibTeX is at index 5
                    elif export_format == "JSON":
                        content = json.dumps([{
                            'title': ref[1],
                            'authors': ref[2],
                            'year': ref[3],
                            'doi': ref[4]
                        } for ref in refs], indent=2)
                    else:
                        content = "\n\n".join([f"{ref[2]} ({ref[3]}). {ref[1]}. DOI: {ref[4]}" for ref in refs])
                    
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    st.success(f"✅ Exported to {export_file.name}")
                except Exception as e:
                    st.error(f"Export error: {str(e)}")
        
        # Display citations
        for i, ref in enumerate(refs, 1):
            with st.expander(f"{i}. {ref[1][:80]}..." if len(ref[1]) > 80 else f"{i}. {ref[1]}"):
                st.write(f"**Authors:** {ref[2]}")
                st.write(f"**Year:** {ref[3]}")
                if ref[4]:
                    st.write(f"**DOI:** {ref[4]}")
                if ref[5]:
                    st.code(ref[5], language=None)
                
    except Exception as e:
        st.error(f"Error loading library: {str(e)}")
        logger.error(f"Library error: {e}")

def main():
    st.header("📚 Citation & Reference Manager")
    st.write("Professional citation tool supporting multiple formats including APA, MLA, IEEE, Chicago, Springer, Harvard, Vancouver, and BibTeX.")
    
    tab1, tab2, tab3 = st.tabs([
        "📝 Manual Entry",
        "🔍 Auto-Fetch",
        "📚 Library"
    ])
    
    with tab1:
        manual_citation_entry()
    
    with tab2:
        auto_fetch_citation()
    
    with tab3:
        citation_library()