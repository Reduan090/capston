# modules/ai_writer.py
import streamlit as st
from utils.llm import ask_llm
from utils.user_data import (
    require_authentication,
    get_user_export_dir,
    get_current_user_id,
    log_user_action,
    list_user_files
)
from config import logger
import subprocess
from pathlib import Path

@require_authentication
def main():
    st.header("✍️ AI Writer & Outline Generator")
    
    # Create tabs for better UX
    tab1, tab2, tab3 = st.tabs(["📝 Generate", "📚 My Exports", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Generate Content")
        
        title = st.text_input("📌 Title", placeholder="Enter your research title...")
        keywords = st.text_input("🔑 Keywords", placeholder="machine learning, AI, neural networks...")
        section = st.text_area("📄 Co-write section (optional)", 
                               placeholder="Paste existing text to continue writing...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Generate Outline", use_container_width=True):
                if not title:
                    st.error("Please enter a title")
                else:
                    with st.spinner("Generating outline..."):
                        prompt = f"Generate a detailed academic outline for '{title}' with keywords: {keywords}. Use formal tone."
                        try:
                            outline = ask_llm(prompt)
                            st.session_state.outline = outline
                            log_user_action("generate_outline", f"title={title}")
                            st.markdown(outline)
                            
                            # Auto-save option
                            if st.checkbox("💾 Save outline"):
                                export_dir = get_user_export_dir()
                                outline_path = export_dir / f"{title}_outline.md"
                                with open(outline_path, "w", encoding="utf-8") as f:
                                    f.write(outline)
                                st.success(f"Saved to {outline_path.name}")
                                log_user_action("save_outline", f"filename={outline_path.name}")
                                
                        except ValueError as e:
                            st.error(f"❌ Error: {str(e)}")
                            logger.error(f"Outline generation error: {e}")
        
        with col2:
            if st.button("📄 Generate Article", use_container_width=True):
                if not title:
                    st.error("Please enter a title")
                else:
                    with st.spinner("Generating full article... This may take a minute..."):
                        section_text = f" Continue from: {section}" if section else ""
                        prompt = f"Write a full academic article for '{title}' with keywords {keywords}.{section_text} Use academic tone with proper citations."
                        try:
                            article = ask_llm(prompt)
                            st.session_state.article = article
                            log_user_action("generate_article", f"title={title} length={len(article)}")
                            
                            st.markdown("### Generated Article")
                            st.markdown(article)
                            
                            # Auto-save
                            export_dir = get_user_export_dir()
                            article_path = export_dir / f"{title}_article.md"
                            with open(article_path, "w", encoding="utf-8") as f:
                                f.write(article)
                            st.success(f"✅ Article generated and saved to {article_path.name}")
                            log_user_action("save_article", f"filename={article_path.name}")
                            
                        except ValueError as e:
                            st.error(f"❌ Error: {str(e)}")
                            logger.error(f"Article generation error: {e}")
        
        st.divider()
        
        # Export section
        st.subheader("📤 Export Options")
        
        if 'article' in st.session_state:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Export to LaTeX", use_container_width=True):
                    export_dir = get_user_export_dir()
                    md_path = export_dir / f"{title}_article.md"
                    tex_path = export_dir / f"{title}_article.tex"
                    
                    try:
                        # Save markdown first
                        with open(md_path, "w", encoding="utf-8") as f:
                            f.write(st.session_state.article)
                        
                        # Convert to LaTeX using pandoc
                        subprocess.run(["pandoc", str(md_path), "-o", str(tex_path)], 
                                     check=True, capture_output=True)
                        st.success(f"✅ Exported to {tex_path.name}")
                        log_user_action("export_latex", f"filename={tex_path.name}")
                        
                    except FileNotFoundError:
                        st.error("❌ Pandoc not installed. Please install pandoc for LaTeX export.")
                    except Exception as e:
                        st.error(f"❌ Export failed: {str(e)}")
                        logger.error(f"LaTeX export error: {e}")
            
            with col2:
                if st.button("📝 Download Markdown", use_container_width=True):
                    st.download_button(
                        label="⬇️ Download .md",
                        data=st.session_state.article,
                        file_name=f"{title}_article.md",
                        mime="text/markdown"
                    )
            
            with col3:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.code(st.session_state.article, language="markdown")
                    st.info("👆 Text ready to copy")
        else:
            st.info("💡 Generate an article first to unlock export options")
    
    with tab2:
        st.subheader("📚 My Exported Files")
        
        export_dir = get_user_export_dir()
        files = list_user_files(extension=".md") + list_user_files(extension=".tex")
        
        if files:
            for file in files:
                with st.expander(f"📄 {file.name}"):
                    st.text(f"Size: {file.stat().st_size / 1024:.2f} KB")
                    st.text(f"Modified: {file.stat().st_mtime}")
                    
                    if st.button(f"🗑️ Delete {file.name}", key=f"del_{file.name}"):
                        file.unlink()
                        st.success(f"Deleted {file.name}")
                        st.rerun()
        else:
            st.info("No exports yet. Generate and save content in the Generate tab.")
    
    with tab3:
        st.subheader("⚙️ Generation Settings")
        
        st.slider("📏 Max Article Length", 1000, 5000, 3000, help="Approximate word count")
        st.selectbox("🎨 Writing Style", ["Academic", "Technical", "Review Paper", "Survey"])
        st.checkbox("📚 Include Citations", value=True)
        st.info("⚠️ Settings coming soon - currently in development")