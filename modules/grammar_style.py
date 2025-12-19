# modules/grammar_style.py
import streamlit as st
from utils.llm import ask_llm
from config import logger
import re

def count_words(text):
    """Count words in text"""
    return len(re.findall(r'\b\w+\b', text))

def grammar_check_enhanced(text):
    """Enhanced grammar checking with detailed feedback"""
    prompt = f"""Perform a comprehensive grammar and style check on this academic text:

Text: {text}

Provide:
1. **Corrected Version**: The text with all corrections applied
2. **Major Issues**: List critical grammar/style problems found
3. **Suggestions**: Recommendations for improving academic writing quality
4. **Readability Score**: Rate readability (1-10) and explain

Format clearly with sections."""
    
    return ask_llm(prompt, temperature=0.2)

def paraphrase_advanced(text, style="Academic"):
    """Advanced paraphrasing with style options"""
    style_prompts = {
        "Academic": "Paraphrase in formal academic style suitable for research papers",
        "Simple": "Paraphrase using simpler language while maintaining meaning",
        "Technical": "Paraphrase with enhanced technical precision",
        "Concise": "Paraphrase more concisely without losing key information"
    }
    
    prompt = f"""{style_prompts[style]}:

Original: {text}

Provide:
1. **Paraphrased Version**: The rewritten text
2. **Key Changes**: Main modifications made
3. **Preserved Meaning**: Confirm meaning is unchanged

Ensure the paraphrase is original and not plagiarized."""
    
    return ask_llm(prompt, temperature=0.6)

def improve_academic_writing(text):
    """Improve academic writing style"""
    prompt = f"""Transform this text into high-quality academic writing suitable for top-tier journals:

Text: {text}

Improve:
- Sentence structure and flow
- Academic vocabulary and terminology
- Clarity and precision
- Formal tone
- Logical transitions

Provide:
1. **Improved Version**
2. **Specific Improvements Made**
3. **Writing Quality Score** (1-10)"""
    
    return ask_llm(prompt, temperature=0.3)

def translate_to_academic_english(text, source_lang="Auto-detect"):
    """Translate and adapt to academic English"""
    prompt = f"""Translate this text {f'from {source_lang}' if source_lang != 'Auto-detect' else ''} to academic English suitable for international journals:

Text: {text}

Requirements:
- Perfect English grammar
- Academic vocabulary and style
- Natural flow appropriate for research papers
- Maintain technical accuracy

Provide the translated version."""
    
    return ask_llm(prompt, temperature=0.4)

def check_consistency(text):
    """Check for consistency in terminology, formatting, and style"""
    prompt = f"""Analyze this text for consistency issues:

Text: {text}

Check for:
1. **Terminology Consistency**: Are terms used consistently?
2. **Tense Consistency**: Is verb tense consistent?
3. **Voice Consistency**: Active vs passive voice patterns
4. **Formatting**: Capitalization, numbering, citations
5. **Style**: Formal/informal mixing

Provide detailed feedback with examples."""
    
    return ask_llm(prompt, temperature=0.3)

def enhance_clarity(text):
    """Enhance clarity and reduce ambiguity"""
    prompt = f"""Enhance the clarity of this text by:
- Removing ambiguities
- Simplifying complex sentences
- Improving logical flow
- Strengthening argument structure

Original: {text}

Provide:
1. **Enhanced Version**
2. **Clarity Improvements**: Specific changes that improved clarity
3. **Remaining Issues**: Any clarity concerns that remain"""
    
    return ask_llm(prompt, temperature=0.3)

def tone_adjuster(text, target_tone):
    """Adjust tone of text"""
    tone_descriptions = {
        "Formal": "highly formal and professional",
        "Neutral": "balanced and objective",
        "Persuasive": "convincing and compelling",
        "Explanatory": "clear and educational"
    }
    
    prompt = f"""Adjust the tone of this text to be {tone_descriptions[target_tone]}:

Original: {text}

Provide the adjusted version while maintaining the core message."""
    
    return ask_llm(prompt, temperature=0.4)

def main():
    st.header("✍️ Advanced Grammar & Style Tools")
    st.write("Enhance your academic writing with AI-powered grammar checking, paraphrasing, and style improvement.")
    
    # Text input with word count
    text = st.text_area(
        "Input Text",
        height=200,
        placeholder="Paste your text here for analysis and improvement...",
        help="Enter the text you want to improve"
    )
    
    if text:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", count_words(text))
        with col2:
            st.metric("Characters", len(text))
        with col3:
            st.metric("Sentences", text.count('.') + text.count('!') + text.count('?'))
    
    # Main tools in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✅ Grammar Check",
        "🔄 Paraphrase",
        "🎯 Academic Style",
        "🌍 Translate",
        "🔧 Advanced Tools"
    ])
    
    # Tab 1: Grammar Check
    with tab1:
        st.write("### Comprehensive Grammar & Style Check")
        st.write("Get detailed feedback on grammar, punctuation, style, and readability.")
        
        if st.button("🔍 Check Grammar & Style", key="grammar_check"):
            if not text:
                st.warning("Please enter text to check.")
            else:
                with st.spinner("Analyzing text..."):
                    try:
                        result = grammar_check_enhanced(text)
                        st.markdown(result)
                        
                        # Option to accept changes
                        if st.button("📋 Copy Corrected Version"):
                            st.info("Corrected version is shown above. Use your browser's copy function.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        logger.error(f"Grammar check error: {e}")
    
    # Tab 2: Paraphrase
    with tab2:
        st.write("### Advanced Paraphrasing")
        st.write("Rewrite text while preserving meaning.")
        
        paraphrase_style = st.selectbox(
            "Paraphrasing Style",
            ["Academic", "Simple", "Technical", "Concise"],
            help="Choose how you want the text rewritten"
        )
        
        if st.button("🔄 Paraphrase", key="paraphrase_btn"):
            if not text:
                st.warning("Please enter text to paraphrase.")
            else:
                with st.spinner("Paraphrasing..."):
                    try:
                        result = paraphrase_advanced(text, paraphrase_style)
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        logger.error(f"Paraphrase error: {e}")
    
    # Tab 3: Academic Style
    with tab3:
        st.write("### Academic Writing Enhancement")
        st.write("Transform your text into high-quality academic writing.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 Improve Academic Style", key="improve_academic"):
                if not text:
                    st.warning("Please enter text to improve.")
                else:
                    with st.spinner("Enhancing academic style..."):
                        try:
                            result = improve_academic_writing(text)
                            st.markdown(result)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            logger.error(f"Academic improvement error: {e}")
        
        with col2:
            if st.button("🎯 Enhance Clarity", key="enhance_clarity"):
                if not text:
                    st.warning("Please enter text to enhance.")
                else:
                    with st.spinner("Enhancing clarity..."):
                        try:
                            result = enhance_clarity(text)
                            st.markdown(result)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            logger.error(f"Clarity enhancement error: {e}")
    
    # Tab 4: Translate
    with tab4:
        st.write("### Translation to Academic English")
        st.write("Translate text to academic English suitable for international journals.")
        
        source_language = st.selectbox(
            "Source Language",
            ["Auto-detect", "Spanish", "French", "German", "Chinese", "Arabic", "Russian", "Portuguese", "Japanese", "Korean"],
            help="Select the source language or use auto-detect"
        )
        
        if st.button("🌍 Translate to Academic English", key="translate_btn"):
            if not text:
                st.warning("Please enter text to translate.")
            else:
                with st.spinner("Translating..."):
                    try:
                        result = translate_to_academic_english(text, source_language)
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        logger.error(f"Translation error: {e}")
    
    # Tab 5: Advanced Tools
    with tab5:
        st.write("### Advanced Analysis Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Consistency Check")
            if st.button("🔍 Check Consistency", key="consistency"):
                if not text:
                    st.warning("Please enter text to check.")
                else:
                    with st.spinner("Checking consistency..."):
                        try:
                            result = check_consistency(text)
                            st.markdown(result)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            logger.error(f"Consistency check error: {e}")
        
        with col2:
            st.write("#### Tone Adjustment")
            target_tone = st.selectbox(
                "Target Tone",
                ["Formal", "Neutral", "Persuasive", "Explanatory"]
            )
            if st.button("🎭 Adjust Tone", key="tone"):
                if not text:
                    st.warning("Please enter text to adjust.")
                else:
                    with st.spinner("Adjusting tone..."):
                        try:
                            result = tone_adjuster(text, target_tone)
                            st.markdown(result)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            logger.error(f"Tone adjustment error: {e}")
        
        st.write("---")
        st.write("#### Batch Processing")
        st.info("💡 Tip: For multiple documents, process them one at a time and save results.")