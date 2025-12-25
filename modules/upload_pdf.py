# modules/upload_pdf.py
import streamlit as st
from pathlib import Path
from utils.document_handler import load_document, chunk_text, create_vector_store
from utils.database import add_reference  # For metadata
from utils.user_data import (
    require_authentication, 
    get_user_upload_dir, 
    get_user_vector_db_dir,
    log_user_action,
    get_current_user_id,
    get_user_storage_stats
)
from config import logger

@require_authentication
def main():
    st.header("📄 Upload Document")
    
    # Show user storage stats
    stats = get_user_storage_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Uploaded Files", stats.get("upload_count", 0))
    with col2:
        st.metric("Storage Used", f"{stats.get('upload_size_mb', 0):.2f} MB")
    with col3:
        st.metric("Vector DBs", stats.get("vector_db_count", 0))
    
    st.divider()
    
    uploaded_file = st.file_uploader("Upload PDF/DOCX/TXT/LaTeX", type=["pdf", "docx", "txt", "tex"])
    
    if uploaded_file:
        # Get user-specific upload directory
        user_upload_dir = get_user_upload_dir()
        file_path = user_upload_dir / uploaded_file.name
        
        # Save file to user's directory
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        log_user_action("upload_file", f"filename={uploaded_file.name} size={uploaded_file.size}")
        
        try:
            with st.spinner("Processing document..."):
                text, metadata = load_document(file_path)
                chunks = chunk_text(text)
                
                # Create vector store in user-specific directory
                user_vdb_dir = get_user_vector_db_dir()
                create_vector_store(chunks, uploaded_file.name, store_dir=user_vdb_dir)
                
                # Add to DB if metadata available
                if metadata.get("title"):
                    add_reference(
                        metadata.get("title", uploaded_file.name),
                        metadata.get("author", "Unknown"),
                        metadata.get("creationDate", "Unknown")[:4],  # Year approx
                        metadata.get("doi", ""),
                        ""  # BibTeX placeholder
                    )
                
                log_user_action("document_processed", f"filename={uploaded_file.name} chunks={len(chunks)}")
                
            st.success(f"✅ Document processed successfully!")
            st.info(f"📊 {len(chunks)} text chunks created and vectorized")
            
            # Show document preview
            with st.expander("📖 Document Preview"):
                st.text(text[:1000] + "..." if len(text) > 1000 else text)
            
        except ValueError as e:
            st.error(f"❌ Error: {str(e)}")
            logger.error(f"Document processing error: {e}")
            log_user_action("upload_error", f"filename={uploaded_file.name} error={str(e)}")