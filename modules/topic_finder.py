# modules/topic_finder.py
import streamlit as st
from pathlib import Path
from utils.document_handler import load_document
from utils.nlp_helpers import extract_topics
from utils.llm import ask_llm, get_embeddings
from utils.api_helpers import fetch_papers
from config import UPLOAD_DIR, logger
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_trending_topics_by_domain():
    """Get trending research topics by domain"""
    st.write("### 🌟 Trending Research Topics")
    
    domains = {
        "Computer Science": ["machine learning", "artificial intelligence", "cybersecurity", "blockchain", "quantum computing"],
        "Medicine & Health": ["personalized medicine", "immunotherapy", "mental health", "telemedicine", "genomics"],
        "Engineering": ["renewable energy", "nanotechnology", "robotics", "smart materials", "sustainable design"],
        "Social Sciences": ["behavioral economics", "social media impact", "climate change policy", "inequality", "digital transformation"],
        "Natural Sciences": ["climate change", "biodiversity", "quantum physics", "astrobiology", "materials science"],
        "Business": ["digital marketing", "fintech", "sustainable business", "entrepreneurship", "supply chain optimization"],
        "Education": ["online learning", "educational technology", "inclusive education", "learning analytics", "skill development"]
    }
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_domain = st.selectbox("Select Research Domain", list(domains.keys()))
    with col2:
        year_filter = st.selectbox("Time Period", ["Last Year", "Last 3 Years", "Last 5 Years", "All Time"])
    
    if st.button("🔍 Explore Trending Topics"):
        with st.spinner(f"Finding trending topics in {selected_domain}..."):
            trending = domains[selected_domain]
            
            st.write(f"#### Top Trending Topics in {selected_domain}")
            
            for i, topic in enumerate(trending, 1):
                with st.expander(f"{i}. {topic.title()} 📈"):
                    # Fetch recent papers on this topic
                    try:
                        papers = fetch_papers(topic, limit=5)
                        if papers:
                            st.write(f"**Recent Research ({len(papers)} papers):**")
                            for paper in papers[:3]:
                                st.write(f"- {paper.get('title', 'Untitled')}")
                                if paper.get('year'):
                                    st.caption(f"Year: {paper['year']}")
                        
                        # Generate research directions
                        prompt = f"""Based on current trends in {selected_domain}, suggest 3 specific research directions for the topic: {topic}.
                        
For each direction provide:
1. Research question
2. Why it's important
3. Potential methodology

Format as bullet points."""
                        
                        suggestions = ask_llm(prompt, temperature=0.7)
                        st.write("**Research Directions:**")
                        st.markdown(suggestions)
                        
                    except Exception as e:
                        st.write("Could not fetch recent papers.")
                        logger.error(f"Error fetching papers for {topic}: {e}")

def extract_topics_from_document():
    """Extract and analyze topics from uploaded documents"""
    st.write("### 📄 Document Topic Analysis")
    
    files = [f for f in UPLOAD_DIR.iterdir() if f.is_file() and f.suffix.lower() in ['.pdf', '.docx', '.txt', '.tex']]
    
    if not files:
        st.info("No uploaded documents found. Upload documents in the 'Upload Document' tab.")
        return
    
    selected_file = st.selectbox("Select Document", [f.name for f in files], key="topic_file_select")
    
    col1, col2 = st.columns(2)
    with col1:
        num_topics = st.slider("Number of topics to extract", 5, 30, 10)
    with col2:
        analysis_depth = st.selectbox("Analysis Depth", ["Quick", "Standard", "Deep"])
    
    if selected_file and st.button("🔍 Extract Topics"):
        file_path = UPLOAD_DIR / selected_file
        
        with st.spinner("Analyzing document..."):
            try:
                text, metadata = load_document(file_path)
                
                # Limit text based on analysis depth
                depth_limits = {"Quick": 10000, "Standard": 50000, "Deep": 200000}
                text_to_analyze = text[:depth_limits[analysis_depth]]
                
                # Extract topics using NLP
                topics = extract_topics(text_to_analyze, top_n=num_topics)
                
                if not topics:
                    st.warning("Could not extract topics. Document may be too short or complex.")
                    return
                
                # Display topics
                st.write(f"#### Extracted {len(topics)} Topics:")
                
                # Create columns for topics
                cols = st.columns(3)
                for i, topic in enumerate(topics):
                    with cols[i % 3]:
                        st.button(f"🏷️ {topic}", key=f"topic_{i}", disabled=True)
                
                # Advanced analysis
                st.write("---")
                st.write("#### 🔬 Advanced Topic Analysis")
                
                # Generate topic relationships using LLM
                prompt = f"""Analyze these topics extracted from a research document and:
1. Group them into 3-4 main themes
2. Identify the primary research focus
3. Suggest related research areas not covered

Topics: {', '.join(topics)}

Format as:
**Main Themes:**
- Theme 1: [topics]
- Theme 2: [topics]

**Primary Focus:** [description]

**Related Research Areas:** [suggestions]"""
                
                analysis = ask_llm(prompt, temperature=0.4)
                st.markdown(analysis)
                
                # Topic similarity to trending research
                st.write("---")
                st.write("#### 🌐 Similarity to Trending Research")
                
                # Get embeddings for extracted topics
                topic_text = " ".join(topics)
                topic_emb = get_embeddings([topic_text])
                
                # Compare with some trending topics
                trending_keywords = [
                    "artificial intelligence machine learning",
                    "climate change sustainability",
                    "healthcare medicine genomics",
                    "quantum computing technology",
                    "social media digital transformation"
                ]
                
                trending_embs = get_embeddings(trending_keywords)
                
                if topic_emb and trending_embs:
                    similarities = cosine_similarity([topic_emb[0]], trending_embs)[0]
                    
                    # Create a simple bar chart
                    st.write("Relevance to trending areas:")
                    for keyword, sim in zip(trending_keywords, similarities):
                        relevance = f"{sim * 100:.1f}%"
                        st.progress(float(sim), text=f"{keyword.title()}: {relevance}")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Topic extraction error: {e}")

def suggest_research_topics():
    """AI-powered research topic suggestions"""
    st.write("### 💡 AI Research Topic Suggestions")
    
    col1, col2 = st.columns(2)
    with col1:
        research_area = st.text_input("Research Area/Field", placeholder="e.g., Machine Learning, Climate Science")
    with col2:
        interest_level = st.selectbox("Research Level", ["Undergraduate", "Masters", "PhD", "Postdoc"])
    
    interests = st.text_area(
        "Specific Interests (optional)",
        placeholder="e.g., I'm interested in applications of AI in healthcare, particularly diagnosis..."
    )
    
    if st.button("✨ Generate Topic Suggestions"):
        if not research_area:
            st.warning("Please enter a research area.")
            return
            
        with st.spinner("Generating personalized topic suggestions..."):
            prompt = f"""Generate 5 novel and specific research topics for {interest_level} level research in {research_area}.

{f'Additional interests: {interests}' if interests else ''}

For each topic provide:
1. **Title**: A clear, specific research title
2. **Research Question**: The main question to investigate
3. **Significance**: Why this research matters
4. **Feasibility**: Why it's appropriate for {interest_level} level
5. **Key References**: Suggested areas to review

Make topics current, feasible, and impactful."""
            
            suggestions = ask_llm(prompt, temperature=0.8)
            st.markdown(suggestions)
            
            # Option to search related papers
            if st.button("🔍 Find Related Papers"):
                with st.spinner("Searching..."):
                    try:
                        papers = fetch_papers(research_area, limit=10)
                        if papers:
                            st.write(f"#### Found {len(papers)} Related Papers:")
                            for paper in papers[:5]:
                                with st.expander(f"📄 {paper.get('title', 'Untitled')[:80]}..."):
                                    st.write(f"**Year:** {paper.get('year', 'N/A')}")
                                    authors = paper.get('authors', [])
                                    if authors:
                                        st.write(f"**Authors:** {', '.join([a.get('name', '') for a in authors[:3]])}")
                                    if paper.get('abstract'):
                                        st.write(f"**Abstract:** {paper['abstract'][:300]}...")
                    except Exception as e:
                        st.warning("Could not fetch papers.")
                        logger.error(f"Paper fetch error: {e}")

def main():
    st.header("🔬 Topic Finder & Research Trends")
    st.write("Discover trending research topics, analyze document themes, and get AI-powered research suggestions.")
    
    tab1, tab2, tab3 = st.tabs([
        "🌟 Trending Topics",
        "📄 Document Analysis", 
        "💡 Topic Suggestions"
    ])
    
    with tab1:
        get_trending_topics_by_domain()
    
    with tab2:
        extract_topics_from_document()
    
    with tab3:
        suggest_research_topics()