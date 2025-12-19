# modules/ask_paper.py
import streamlit as st
from pathlib import Path
import numpy as np
from utils.document_handler import load_vector_store
from utils.llm import ask_llm, get_embeddings
from config import UPLOAD_DIR, logger

def main():
    st.header("💬 Ask a Paper (RAG Chat)")
    st.write("Interact with your uploaded documents using advanced RAG (Retrieval-Augmented Generation)")
    
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.suffix.lower() in [".pdf", ".docx", ".txt", ".tex"]]
    
    if not files:
        st.warning("No documents found. Please upload documents first in the 'Upload Document' tab.")
        return
    
    # Document selection with multi-select for cross-document queries
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_file = st.selectbox("📄 Select Document", files, key="askpaper_file_select")
    with col2:
        multi_doc = st.checkbox("Multi-doc", help="Query across multiple documents")
    
    if multi_doc:
        selected_files = st.multiselect(
            "Select multiple documents",
            files,
            default=[selected_file] if selected_file else []
        )
    else:
        selected_files = [selected_file] if selected_file else []
    
    if not selected_files:
        return
        
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        num_chunks = st.slider("Number of context chunks to retrieve", 3, 15, 5)
        temperature = st.slider("Response creativity (temperature)", 0.0, 1.0, 0.3, 0.1)
        answer_style = st.selectbox(
            "Answer Style",
            ["Concise", "Detailed", "Academic", "Simple Explanation"],
            help="Choose how the answer should be formatted"
        )
    
    # Initialize or retrieve chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    st.write("### 💭 Conversation")
    for i, chat in enumerate(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(chat['question'])
        with st.chat_message("assistant"):
            st.write(chat['answer'])
            if 'sources' in chat:
                with st.expander("📚 View Sources"):
                    for j, source in enumerate(chat['sources'], 1):
                        st.text(f"{j}. {source[:200]}...")
    
    # Question input
    question = st.chat_input("Ask a question about the document(s)...")
    
    # Quick question buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Summarize"):
            question = "Provide a comprehensive summary of this document."
    with col2:
        if st.button("🎯 Key Points"):
            question = "What are the main key points and findings?"
    with col3:
        if st.button("🔬 Methodology"):
            question = "Explain the methodology used in this research."
    
    if question:
        with st.spinner("Searching and analyzing..."):
            try:
                all_relevant = []
                all_chunks = []
                
                # Load vector stores for selected documents
                for filename in selected_files:
                    try:
                        index, chunks = load_vector_store(filename)
                        all_chunks.extend([(chunk, filename) for chunk in chunks])
                        
                        # Get embeddings and search
                        query_emb = get_embeddings([question])[0]
                        query_emb_array = np.array([query_emb]).astype('float32')
                        D, I = index.search(query_emb_array, k=num_chunks)
                        
                        # Collect relevant chunks with metadata
                        for idx, score in zip(I[0], D[0]):
                            if idx < len(chunks):
                                all_relevant.append({
                                    'text': chunks[idx],
                                    'file': filename,
                                    'score': float(score)
                                })
                    except Exception as e:
                        st.warning(f"Could not process {filename}: {str(e)}")
                        logger.error(f"Error loading {filename}: {e}")
                
                if not all_relevant:
                    st.error("Could not retrieve relevant context. Please ensure documents are processed.")
                    return
                
                # Sort by relevance score
                all_relevant.sort(key=lambda x: x['score'])
                top_relevant = all_relevant[:num_chunks]
                
                # Build context
                context = "\n\n".join([f"[From {r['file']}]\n{r['text']}" for r in top_relevant])
                
                # Style-specific prompts
                style_prompts = {
                    "Concise": "Provide a brief, direct answer in 2-3 sentences.",
                    "Detailed": "Provide a comprehensive, detailed answer with explanations.",
                    "Academic": "Provide a formal, academic-style answer with proper terminology.",
                    "Simple Explanation": "Explain in simple terms as if teaching a beginner."
                }
                
                # Generate answer
                prompt = f"""Based on the following context from the document(s), answer this question: "{question}"

Context:
{context}

Instructions: {style_prompts.get(answer_style, '')}
Provide an accurate answer based ONLY on the context provided. If the answer is not in the context, say so.

Answer:"""
                
                answer = ask_llm(prompt, temperature=temperature)
                
                # Display answer
                with st.chat_message("user"):
                    st.write(question)
                
                with st.chat_message("assistant"):
                    st.write(answer)
                    
                    # Show sources
                    with st.expander("📚 View Retrieved Context"):
                        for i, rel in enumerate(top_relevant, 1):
                            st.write(f"**Source {i}** (from {rel['file']}, relevance: {rel['score']:.3f})")
                            st.text(rel['text'][:300] + "...")
                            st.divider()
                
                # Save to history
                st.session_state.chat_history.append({
                    'question': question,
                    'answer': answer,
                    'sources': [r['text'] for r in top_relevant],
                    'files': selected_files
                })
                
                # Clear button
                if len(st.session_state.chat_history) > 0:
                    if st.button("🗑️ Clear Conversation"):
                        st.session_state.chat_history = []
                        st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Ask paper error: {e}")