# modules/plagiarism_check.py
import streamlit as st
from utils.llm import get_embeddings, ask_llm
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from config import logger, UPLOAD_DIR, EXPORT_DIR
from utils.document_handler import load_document, chunk_text
import numpy as np
import re
from collections import defaultdict
from datetime import datetime

def split_into_sentences(text: str) -> list:
    """Split text into sentences for granular plagiarism detection."""
    # Enhanced sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

def split_into_paragraphs(text: str) -> list:
    """Split text into paragraphs."""
    paragraphs = re.split(r'\n\s*\n', text.strip())
    return [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 50]

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate overall similarity between two texts."""
    try:
        emb1 = get_embeddings([text1])
        emb2 = get_embeddings([text2])
        if not emb1 or not emb2:
            return 0.0
        sim = cosine_similarity([emb1[0]], [emb2[0]])[0][0]
        return float(sim)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return 0.0

def sentence_level_analysis(original: str, checked: str, threshold=0.70) -> tuple:
    """Analyze similarity at sentence level to detect paraphrasing."""
    orig_sentences = split_into_sentences(original)
    check_sentences = split_into_sentences(checked)
    
    if not orig_sentences or not check_sentences:
        return [], 0.0
    
    try:
        orig_embs = get_embeddings(orig_sentences)
        check_embs = get_embeddings(check_sentences)
        
        if not orig_embs or not check_embs:
            return [], 0.0
        
        # Compare each checked sentence against all original sentences
        results = []
        for i, check_emb in enumerate(check_embs):
            similarities = cosine_similarity([check_emb], orig_embs)[0]
            max_sim = float(np.max(similarities))
            max_idx = int(np.argmax(similarities))
            
            # Categorize severity
            if max_sim > 0.90:
                severity = "Critical"
                color = "error"
            elif max_sim > 0.80:
                severity = "High"
                color = "warning"
            elif max_sim > threshold:
                severity = "Medium"
                color = "info"
            else:
                severity = "Low"
                color = "success"
            
            results.append({
                'checked_sent': check_sentences[i],
                'original_sent': orig_sentences[max_idx],
                'similarity': max_sim,
                'is_plagiarized': max_sim > threshold,
                'severity': severity,
                'color': color
            })
        
        avg_sim = np.mean([r['similarity'] for r in results])
        return results, float(avg_sim)
    except Exception as e:
        logger.error(f"Sentence analysis error: {e}")
        return [], 0.0

def paragraph_level_analysis(original: str, checked: str) -> dict:
    """Analyze similarity at paragraph level for structural plagiarism."""
    orig_paragraphs = split_into_paragraphs(original)
    check_paragraphs = split_into_paragraphs(checked)
    
    if not orig_paragraphs or not check_paragraphs:
        return {}
    
    try:
        results = {
            'paragraphs_checked': len(check_paragraphs),
            'paragraphs_original': len(orig_paragraphs),
            'matches': []
        }
        
        # Get embeddings
        orig_embs = get_embeddings(orig_paragraphs)
        check_embs = get_embeddings(check_paragraphs)
        
        if not orig_embs or not check_embs:
            return results
        
        # Find paragraph matches
        for i, check_emb in enumerate(check_embs):
            similarities = cosine_similarity([check_emb], orig_embs)[0]
            max_sim = float(np.max(similarities))
            max_idx = int(np.argmax(similarities))
            
            if max_sim > 0.65:  # Threshold for paragraph match
                results['matches'].append({
                    'paragraph_num': i + 1,
                    'similarity': max_sim,
                    'checked_para': check_paragraphs[i][:200] + "...",
                    'original_para': orig_paragraphs[max_idx][:200] + "..."
                })
        
        return results
    except Exception as e:
        logger.error(f"Paragraph analysis error: {e}")
        return {}

def check_against_database(checked_text: str, chunk_size=500) -> dict:
    """Advanced check against uploaded documents with chunk-level analysis."""
    try:
        results = defaultdict(list)
        
        upload_dir = Path(UPLOAD_DIR)
        if not upload_dir.exists():
            return {}
        
        # Get embeddings for checked text chunks
        checked_chunks = chunk_text(checked_text)
        if not checked_chunks:
            return {}
        
        checked_embs = get_embeddings(checked_chunks)
        if not checked_embs:
            return {}
        
        # Check against each document
        for file_path in upload_dir.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt', '.docx', '.tex']:
                try:
                    text, _ = load_document(file_path)
                    if not text:
                        continue
                    
                    # Chunk the document
                    doc_chunks = chunk_text(text)
                    if not doc_chunks:
                        continue
                    
                    doc_embs = get_embeddings(doc_chunks)
                    if not doc_embs:
                        continue
                    
                    # Find matching chunks
                    for i, checked_emb in enumerate(checked_embs):
                        similarities = cosine_similarity([checked_emb], doc_embs)[0]
                        max_sim = float(np.max(similarities))
                        max_idx = int(np.argmax(similarities))
                        
                        if max_sim > 0.70:  # Threshold for match
                            results[file_path.name].append({
                                'chunk_num': i + 1,
                                'similarity': max_sim,
                                'checked_chunk': checked_chunks[i],
                                'matched_chunk': doc_chunks[max_idx]
                            })
                
                except Exception as e:
                    logger.error(f"Error checking {file_path.name}: {e}")
                    continue
        
        return dict(results)
    except Exception as e:
        logger.error(f"Database check error: {e}")
        return {}

def detect_paraphrasing(text: str) -> dict:
    """Use LLM to detect sophisticated paraphrasing patterns."""
    try:
        prompt = f"""Analyze this text for signs of paraphrasing or text spinning:

Text: {text[:2000]}

Look for:
1. Awkward synonym substitutions
2. Unnatural sentence structures
3. Inconsistent writing style
4. Passive voice overuse
5. Unusual word choices

Rate the likelihood of paraphrasing (0-100%) and explain your reasoning."""
        
        analysis = ask_llm(prompt, temperature=0.2)
        return {'analysis': analysis}
    except Exception as e:
        logger.error(f"Paraphrasing detection error: {e}")
        return {'analysis': 'Error performing analysis'}

def generate_plagiarism_report(results: dict) -> str:
    """Generate comprehensive plagiarism report."""
    report = f"""# Plagiarism Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Overall Similarity Score**: {results.get('overall_similarity', 0):.1%}
- **Risk Level**: {results.get('risk_level', 'Unknown')}
- **Sentences Analyzed**: {results.get('total_sentences', 0)}
- **Plagiarized Sentences**: {results.get('plagiarized_sentences', 0)}

## Detailed Findings
{results.get('detailed_findings', 'No detailed findings available')}

## Recommendations
{results.get('recommendations', 'No recommendations available')}
"""
    return report

def main():
    st.header("🔍 Advanced Plagiarism Checker (Turnitin-Level)")
    st.write("Professional plagiarism detection with multi-level analysis, paraphrasing detection, and comprehensive reporting.")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Comprehensive Check",
        "🔍 Direct Comparison",
        "📝 Sentence Analysis",
        "🗄️ Database Check",
        "📋 Reports"
    ])
    
    # Tab 1: Comprehensive Check
    with tab1:
        st.write("### 🎯 Complete Plagiarism Analysis")
        st.write("Performs all checks: similarity, paraphrasing detection, and database matching.")
        
        text_to_check = st.text_area(
            "Enter text to check for plagiarism",
            height=250,
            placeholder="Paste your text here for comprehensive plagiarism analysis...",
            key="comprehensive_text"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            sensitivity = st.select_slider(
                "Detection Sensitivity",
                options=["Low (0.80)", "Medium (0.70)", "High (0.60)"],
                value="Medium (0.70)",
                help="Higher sensitivity detects more potential matches but may have false positives"
            )
        with col2:
            include_paraphrase = st.checkbox("Include AI Paraphrasing Detection", value=True)
        
        if st.button("🔍 Run Comprehensive Check", key="comprehensive_check"):
            if not text_to_check or len(text_to_check) < 50:
                st.warning("Please enter at least 50 characters of text.")
            else:
                # Parse sensitivity
                threshold = float(sensitivity.split('(')[1].split(')')[0])
                
                with st.spinner("Analyzing text... This may take a moment."):
                    try:
                        # Initialize results
                        report_data = {
                            'text_length': len(text_to_check),
                            'word_count': len(text_to_check.split()),
                            'total_sentences': len(split_into_sentences(text_to_check))
                        }
                        
                        # 1. Check against database
                        st.write("**Step 1/3:** Checking against uploaded documents...")
                        db_matches = check_against_database(text_to_check)
                        
                        # 2. AI Paraphrasing Detection
                        if include_paraphrase:
                            st.write("**Step 2/3:** Analyzing for paraphrasing patterns...")
                            paraphrase_result = detect_paraphrasing(text_to_check)
                        
                        st.write("**Step 3/3:** Generating comprehensive report...")
                        
                        # Display results
                        st.write("---")
                        st.write("## 📊 Analysis Results")
                        
                        # Overall similarity score
                        if db_matches:
                            max_similarity = max([
                                max([m['similarity'] for m in matches])
                                for matches in db_matches.values()
                            ])
                        else:
                            max_similarity = 0.0
                        
                        # Risk level determination
                        if max_similarity > 0.85:
                            risk_level = "🔴 CRITICAL"
                            risk_color = "error"
                        elif max_similarity > 0.70:
                            risk_level = "🟠 HIGH"
                            risk_color = "warning"
                        elif max_similarity > 0.50:
                            risk_level = "🟡 MEDIUM"
                            risk_color = "info"
                        else:
                            risk_level = "🟢 LOW"
                            risk_color = "success"
                        
                        # Display metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Max Similarity", f"{max_similarity:.1%}")
                        with col2:
                            st.metric("Risk Level", risk_level)
                        with col3:
                            st.metric("Documents Matched", len(db_matches))
                        with col4:
                            st.metric("Words Analyzed", report_data['word_count'])
                        
                        # Database matches
                        if db_matches:
                            st.write("### 🗄️ Database Matches Found")
                            for filename, matches in db_matches.items():
                                avg_sim = np.mean([m['similarity'] for m in matches])
                                with st.expander(f"📄 {filename} - {len(matches)} matches (avg: {avg_sim:.1%})"):
                                    for i, match in enumerate(matches[:5], 1):  # Show top 5
                                        st.write(f"**Match {i}** (Similarity: {match['similarity']:.1%})")
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.text_area("Your Text:", match['checked_chunk'][:200], height=100, key=f"checked_{filename}_{i}", disabled=True)
                                        with col2:
                                            st.text_area("Source Match:", match['matched_chunk'][:200], height=100, key=f"matched_{filename}_{i}", disabled=True)
                        else:
                            st.success("✅ No matches found in uploaded documents database.")
                        
                        # Paraphrasing analysis
                        if include_paraphrase:
                            st.write("### 🔬 AI Paraphrasing Analysis")
                            st.markdown(paraphrase_result.get('analysis', 'No analysis available'))
                        
                        # Recommendations
                        st.write("### 💡 Recommendations")
                        if max_similarity > 0.85:
                            st.error("""
                            **Critical plagiarism detected:**
                            - Review all highlighted sections immediately
                            - Rewrite or properly cite matched content
                            - Consider using plagiarism removal services
                            - Do NOT submit without major revisions
                            """)
                        elif max_similarity > 0.70:
                            st.warning("""
                            **Significant similarity detected:**
                            - Review matched sections carefully
                            - Add proper citations where needed
                            - Paraphrase more thoroughly
                            - Consider rephrasing problematic sentences
                            """)
                        elif max_similarity > 0.50:
                            st.info("""
                            **Moderate similarity:**
                            - Some sections may need revision
                            - Ensure all sources are properly cited
                            - Review paraphrasing techniques
                            """)
                        else:
                            st.success("""
                            **Content appears original:**
                            - Low plagiarism risk detected
                            - Continue with standard citation practices
                            - Verify all direct quotes are cited
                            """)
                        
                        # Export report option
                        if st.button("📥 Generate Detailed Report"):
                            report_data['overall_similarity'] = max_similarity
                            report_data['risk_level'] = risk_level
                            report_data['plagiarized_sentences'] = 0  # Could be calculated
                            report_data['detailed_findings'] = f"Found {len(db_matches)} matching documents"
                            report_data['recommendations'] = "See recommendations above"
                            
                            report = generate_plagiarism_report(report_data)
                            report_file = EXPORT_DIR / f"plagiarism_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                            with open(report_file, 'w', encoding='utf-8') as f:
                                f.write(report)
                            st.success(f"✅ Report saved to {report_file.name}")
                        
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
                        logger.error(f"Comprehensive check error: {e}")
    
    # Tab 2: Direct Comparison
    with tab2:
        st.write("### 📋 Direct Text Comparison")
        st.write("Compare two texts directly to check similarity.")
        
        col1, col2 = st.columns(2)
        with col1:
            original = st.text_area("Original/Source Text", height=250, key="original_direct")
        with col2:
            checked = st.text_area("Text to Check", height=250, key="checked_direct")
        
        if st.button("Compare Texts", key="btn_direct"):
            if original and checked:
                with st.spinner("Analyzing similarity..."):
                    sim = calculate_similarity(original, checked)
                    
                    # Display result
                    col1, col2, col3 = st.columns([2, 2, 3])
                    with col1:
                        st.metric("Similarity Score", f"{sim:.2%}")
                    with col2:
                        if sim > 0.85:
                            st.error("🔴 Critical")
                        elif sim > 0.70:
                            st.warning("🟠 High")
                        elif sim > 0.50:
                            st.info("🟡 Medium")
                        else:
                            st.success("🟢 Low")
                    
                    # Visual similarity bar
                    st.write("### Similarity Visualization")
                    st.progress(float(sim))
                    
                    # Interpretation
                    if sim > 0.85:
                        st.error("""
                        **🔴 CRITICAL SIMILARITY** ({:.1%})
                        - Texts are nearly identical
                        - Direct copying or minimal paraphrasing detected
                        - Requires immediate attention
                        """.format(sim))
                    elif sim > 0.70:
                        st.warning("""
                        **🟠 HIGH SIMILARITY** ({:.1%})
                        - Significant overlap detected
                        - Possible paraphrasing without proper citation
                        - Review and revise recommended
                        """.format(sim))
                    elif sim > 0.50:
                        st.info("""
                        **🟡 MODERATE SIMILARITY** ({:.1%})
                        - Some similarity present
                        - May share common terminology or themes
                        - Check for proper citations
                        """.format(sim))
                    else:
                        st.success("""
                        **🟢 LOW SIMILARITY** ({:.1%})
                        - Texts appear distinct
                        - No significant plagiarism concerns
                        - Continue with standard practices
                        """.format(sim))
            else:
                st.error("Please provide both texts to compare.")
    
    # Tab 3: Sentence-Level Analysis
    with tab3:
        st.write("### 📝 Sentence-by-Sentence Analysis")
        st.write("Detect paraphrasing and identify problematic sentences.")
        
        col1, col2 = st.columns(2)
        with col1:
            original_sent = st.text_area("Original Text", height=250, key="original_sent")
        with col2:
            checked_sent = st.text_area("Text to Check", height=250, key="checked_sent")
        
        threshold_sent = st.slider("Similarity Threshold", 0.5, 0.9, 0.70, 0.05)
        
        if st.button("Analyze Sentences", key="btn_sent"):
            if original_sent and checked_sent:
                with st.spinner("Analyzing sentence-by-sentence..."):
                    results, avg_sim = sentence_level_analysis(original_sent, checked_sent, threshold_sent)
                    
                    if results:
                        # Summary metrics
                        plagiarized_count = sum(1 for r in results if r['is_plagiarized'])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Avg Similarity", f"{avg_sim:.1%}")
                        with col2:
                            st.metric("Sentences Checked", len(results))
                        with col3:
                            st.metric("Flagged Sentences", plagiarized_count)
                        
                        # Display results
                        st.write("### Detailed Analysis")
                        for i, result in enumerate(results, 1):
                            severity = result['severity']
                            sim = result['similarity']
                            
                            if severity == "Critical":
                                icon = "🔴"
                            elif severity == "High":
                                icon = "🟠"
                            elif severity == "Medium":
                                icon = "🟡"
                            else:
                                icon = "🟢"
                            
                            with st.expander(f"{icon} Sentence {i} - {severity} ({sim:.1%})"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Your Sentence:**")
                                    st.info(result['checked_sent'])
                                with col2:
                                    st.write("**Best Match:**")
                                    st.warning(result['original_sent'])
                                
                                if result['is_plagiarized']:
                                    st.error(f"⚠️ **{severity} plagiarism risk detected**")
                                    st.write("**Recommendation:** Rephrase this sentence or add proper citation.")
                                else:
                                    st.success("✅ Acceptable similarity level")
                    else:
                        st.warning("Could not analyze sentences. Ensure both texts have clear sentence boundaries.")
            else:
                st.error("Please provide both texts.")
    
    # Tab 4: Database Check
    with tab4:
        st.write("### 🗄️ Check Against Document Database")
        st.write("Compare your text against all uploaded documents.")
        
        checked_text_db = st.text_area(
            "Text to Check",
            height=250,
            placeholder="Enter text to check against your document database...",
            key="checked_db"
        )
        
        show_details = st.checkbox("Show detailed chunk matches", value=False)
        
        if st.button("🔍 Search Database", key="btn_db"):
            if checked_text_db:
                with st.spinner("Searching through uploaded documents..."):
                    try:
                        matches = check_against_database(checked_text_db)
                        
                        if matches:
                            st.warning(f"⚠️ Found matches in {len(matches)} documents")
                            
                            # Sort by average similarity
                            sorted_matches = []
                            for filename, match_list in matches.items():
                                avg_sim = np.mean([m['similarity'] for m in match_list])
                                sorted_matches.append((filename, match_list, avg_sim))
                            sorted_matches.sort(key=lambda x: x[2], reverse=True)
                            
                            # Display matches
                            for filename, match_list, avg_sim in sorted_matches:
                                max_sim = max([m['similarity'] for m in match_list])
                                
                                with st.expander(f"📄 {filename} - {len(match_list)} matches (max: {max_sim:.1%}, avg: {avg_sim:.1%})"):
                                    if max_sim > 0.85:
                                        st.error("🔴 Critical similarity detected")
                                    elif max_sim > 0.70:
                                        st.warning("🟠 High similarity detected")
                                    else:
                                        st.info("🟡 Moderate similarity detected")
                                    
                                    if show_details:
                                        for i, match in enumerate(match_list[:10], 1):  # Limit to 10
                                            st.write(f"**Match {i}** (Similarity: {match['similarity']:.1%})")
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                st.text_area("Your Text:", match['checked_chunk'][:300], height=120, key=f"db_checked_{filename}_{i}", disabled=True)
                                            with col2:
                                                st.text_area("Source:", match['matched_chunk'][:300], height=120, key=f"db_matched_{filename}_{i}", disabled=True)
                                            st.divider()
                                    else:
                                        st.info("Enable 'Show detailed chunk matches' to see specific text matches.")
                        else:
                            st.success("✅ No significant matches found in the database.")
                            st.info("Your text appears to be original compared to uploaded documents.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        logger.error(f"Database check error: {e}")
            else:
                st.error("Please enter text to check.")
    
    # Tab 5: Reports
    with tab5:
        st.write("### 📋 Plagiarism Reports")
        st.write("View and manage generated plagiarism reports.")
        
        # List report files
        if EXPORT_DIR.exists():
            report_files = list(EXPORT_DIR.glob("plagiarism_report_*.md"))
            
            if report_files:
                st.write(f"**Found {len(report_files)} reports**")
                
                for report_file in sorted(report_files, reverse=True)[:10]:  # Show last 10
                    with st.expander(f"📄 {report_file.name}"):
                        with open(report_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        st.markdown(content)
                        
                        if st.button(f"Delete", key=f"del_{report_file.name}"):
                            report_file.unlink()
                            st.success("Report deleted")
                            st.rerun()
            else:
                st.info("No plagiarism reports found. Run a comprehensive check to generate a report.")
        else:
            st.info("No reports directory found.")