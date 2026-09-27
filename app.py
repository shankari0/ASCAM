import streamlit as st
import os
import uuid
from streamlit_pdf_viewer import pdf_viewer
from modules.pdf_parser import extract_text_and_images
from modules.vlm import image_to_markdown
from modules.rag import build_knowledge_base, retrieve
from modules.llm import summarise, answer_question, generate_flashcards, generate_quiz, extract_key_concepts
from modules.translation import translate
from modules.tts import text_to_speech

st.set_page_config(page_title="ASCAM", layout="wide")
st.title("ASCAM — AI Study Companion for Academic Materials")
st.caption("Upload an academic PDF and use the study features below.")

# ── File Upload ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload a PDF to get started", type="pdf")

if uploaded_file:
    if st.session_state.get("uploaded_filename") != uploaded_file.name:

        doc_id = str(uuid.uuid4())[:8]
        pdf_path = f"uploads/{doc_id}.pdf"
        os.makedirs("uploads", exist_ok=True)

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Extracting text and images from PDF..."):
            raw_text, image_paths = extract_text_and_images(pdf_path)

        st.info(f"Text extracted. Found {len(image_paths)} image(s) in the document.")

        ocr_text = ""
        if image_paths:
            with st.spinner(f"Analysing {len(image_paths)} diagram(s)..."):
                for img_path in image_paths:
                    description = image_to_markdown(img_path)
                    if description:
                        ocr_text += f"\n[Diagram description: {description}]\n"

        full_text = raw_text + "\n\n" + ocr_text
        with st.spinner("Building knowledge base for this document..."):
            num_chunks = build_knowledge_base(doc_id, full_text)

        st.session_state["doc_id"] = doc_id
        st.session_state["full_text"] = full_text
        st.session_state["uploaded_filename"] = uploaded_file.name
        st.session_state["num_chunks"] = num_chunks
        st.session_state["pdf_path"] = pdf_path

        st.success(f"Ready — {num_chunks} chunks indexed in knowledge base.")

    else:
        st.success(f"Document already loaded — {st.session_state['num_chunks']} chunks in knowledge base.")

# ── Main Layout ───────────────────────────────────────────────────────────────
if "doc_id" in st.session_state:
    st.divider()

    # Split into two columns — PDF viewer on left, features on right
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.subheader("Document Viewer")

        tab1, tab2 = st.tabs(["PDF View", "Selectable Text"])

        with tab1:
            pdf_viewer(
                st.session_state["pdf_path"],
                height=650,
                width="100%"
            )

        with tab2:
            st.caption("Select and copy any section of text from here, then paste it into the feature panel on the right.")
            st.text_area(
                "Extracted document text",
                value=st.session_state["full_text"],
                height=650,
                label_visibility="collapsed"
            )

    with right_col:
        st.subheader("Study Features")

        feature = st.selectbox("Choose a study feature", [
            "Summarise",
            "Key Concepts",
            "Ask a Question",
            "Flashcards",
            "Quiz",
            "Translate",
            "Text-to-Speech"
        ])

        doc_id = st.session_state["doc_id"]
        full_text = st.session_state["full_text"]
        short_text = " ".join(full_text.split()[:3000])

        # ── Summarise ─────────────────────────────────────────────────────────
        if feature == "Summarise":
            if st.button("Generate Summary"):
                with st.spinner("Summarising..."):
                    result = summarise(short_text)
                st.subheader("Summary")
                st.write(result)

        # ── Key Concepts ──────────────────────────────────────────────────────
        elif feature == "Key Concepts":
            if st.button("Extract Key Concepts"):
                with st.spinner("Extracting key concepts..."):
                    result = extract_key_concepts(short_text)
                st.subheader("Key Concepts")
                st.write(result)

        # ── Ask a Question ────────────────────────────────────────────────────
        elif feature == "Ask a Question":
            question = st.text_input("Type your question about the document")
            if st.button("Ask") and question:
                with st.spinner("Searching document and generating answer..."):
                    context = retrieve(doc_id, question)
                    result = answer_question(question, context)
                st.subheader("Answer")
                st.write(result)
                with st.expander("View retrieved context from document"):
                    st.write(context)

        # ── Flashcards ────────────────────────────────────────────────────────
        elif feature == "Flashcards":
            num = st.slider("Number of flashcards", 3, 10, 5)
            if st.button("Generate Flashcards"):
                with st.spinner("Generating flashcards..."):
                    context = retrieve(doc_id, "key concepts and definitions")
                    result = generate_flashcards(context, num)
                st.subheader("Flashcards")
                st.write(result)

        # ── Quiz ──────────────────────────────────────────────────────────────
        elif feature == "Quiz":
            num = st.slider("Number of questions", 3, 10, 5)
            if st.button("Generate Quiz"):
                with st.spinner("Generating quiz..."):
                    context = retrieve(doc_id, "key concepts and important facts")
                    result = generate_quiz(context, num)
                st.subheader("Quiz")
                st.write(result)

        # ── Translate ─────────────────────────────────────────────────────────
        elif feature == "Translate":
            st.caption("Copy the section you want from the PDF viewer on the left and paste it below.")

            selected_text = st.text_area(
                "Paste or edit the text you want to translate",
                value="",
                height=150,
                placeholder="Paste the text you want to translate here..."
            )

            lang_options = {
                "French": "fr",
                "German": "de",
                "Chinese": "zh",
                "Spanish": "es",
                "Arabic": "ar"
            }
            lang_name = st.selectbox("Translate to", list(lang_options.keys()))

            if st.button("Translate") and selected_text:
                word_count = len(selected_text.split())
                if word_count > 300:
                    st.warning(f"{word_count} words selected. Translation works best under 300 words.")

                with st.spinner(f"Translating to {lang_name}..."):
                    words = selected_text.split()
                    chunks = [" ".join(words[i:i+200]) for i in range(0, len(words), 200)]
                    translated_chunks = [translate(chunk, lang_options[lang_name]) for chunk in chunks]
                    result = " ".join(translated_chunks)

                st.subheader(f"Translation ({lang_name})")
                st.write(result)

        # ── Text-to-Speech ────────────────────────────────────────────────────
        elif feature == "Text-to-Speech":
            st.caption("Copy the section you want from the PDF viewer on the left and paste it below.")

            selected_text = st.text_area(
                "Paste or edit the text you want to hear",
                value="",
                height=150,
                placeholder="Paste the text you want to convert to audio here..."
            )

            lang_options = {
                "English": ("en-US-AriaNeural", None),
                "French": ("fr-FR-DeniseNeural", "fr"),
                "German": ("de-DE-KatjaNeural", "de"),
                "Chinese": ("zh-CN-XiaoxiaoNeural", "zh"),
                "Spanish": ("es-ES-ElviraNeural", "es"),
                "Arabic": ("ar-EG-SalmaNeural", "ar"),
            }

            lang_name = st.selectbox("Choose language and voice", list(lang_options.keys()))
            voice, lang_code = lang_options[lang_name]

            word_count = len(selected_text.split()) if selected_text else 0
            st.caption(f"Word count: {word_count}")

            if word_count > 500:
                st.warning("Text is quite long. Consider selecting a shorter section for faster audio generation.")

            if st.button("Convert to Audio") and selected_text:
                with st.spinner("Processing..."):
                    if lang_code is not None:
                        words = selected_text.split()
                        chunks = [" ".join(words[i:i+200]) for i in range(0, len(words), 200)]
                        translated_chunks = [translate(chunk, lang_code) for chunk in chunks]
                        text_for_audio = " ".join(translated_chunks)
                    else:
                        text_for_audio = selected_text

                    audio_path = text_to_speech(text_for_audio, voice=voice)

                if lang_code:
                    with st.expander("View translated text"):
                        st.write(text_for_audio)

                st.subheader("Audio Output")
                st.audio(audio_path)
                st.caption("Right-click the audio player to save the file.")