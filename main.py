# import os
# import streamlit as st
# from agent import handle_user_input
# from pdf_processor import process_pdf

# st.title("Your Research Paper Assistant")  # Removed 📘

# # Initialize session state
# st.session_state.setdefault("messages", [])
# st.session_state.setdefault("uploaded_files", [])
# st.session_state.setdefault("awaiting_image_consent", False)
# st.session_state.setdefault("pending_image_paths", [])
# st.session_state.setdefault("pending_image_contexts", [])

# # Display chat history
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Handle user input
# if prompt := st.chat_input("What is up?"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     if st.session_state.awaiting_image_consent:
#         if prompt.strip().lower() in {"yes", "yeah", "ok", "okay", "sure", "yup"}:
#             st.markdown("### Related Images and Their Explanations")  # Removed 🖼️
#             for path, context in zip(
#                 st.session_state.pending_image_paths,
#                 st.session_state.pending_image_contexts,
#             ):
#                 st.image(path, caption=os.path.basename(path))
#                 st.markdown(f"**Explanation:** {context}")
#         else:
#             st.markdown("Got it! No images will be shown.")  # Removed ✅

#         # Reset image-related states
#         st.session_state.awaiting_image_consent = False
#         st.session_state.pending_image_paths = []
#         st.session_state.pending_image_contexts = []

#     else:
#         with st.chat_message("assistant"):
#             placeholder = st.empty()
#             full_response, image_paths, image_contexts = handle_user_input(prompt)
#             placeholder.markdown(full_response)

#         st.session_state.messages.append(
#             {"role": "assistant", "content": full_response}
#         )

#         if image_paths:
#             ask = f"Would you like me to show you the related images from this context? ({len(image_paths)} available)"
#             st.session_state.messages.append({"role": "assistant", "content": ask})
#             with st.chat_message("assistant"):
#                 st.markdown(ask)
#             st.session_state.awaiting_image_consent = True
#             st.session_state.pending_image_paths = image_paths
#             st.session_state.pending_image_contexts = image_contexts

# # Sidebar for PDF upload
# with st.sidebar:
#     uploaded_file = st.file_uploader("Upload PDF", type="pdf")
#     if uploaded_file:
#         st.session_state.uploaded_files.append(uploaded_file)
#         process_pdf(uploaded_file)
#         st.success(f"Uploaded: {uploaded_file.name}")


import os
import streamlit as st
from agent import handle_user_input
from pdf_processor import process_pdf

st.title("Your Research Paper Assistant")  # Removed 📘

# Initialize session state
st.session_state.setdefault("messages", [])
st.session_state.setdefault("uploaded_files", [])
st.session_state.setdefault("awaiting_image_consent", False)
st.session_state.setdefault("pending_image_paths", [])
st.session_state.setdefault("pending_image_contexts", [])

# If there are any messages, add a slider to choose how many to display
if st.session_state.messages:
    num_messages = len(st.session_state.messages)
    num_to_show = st.slider(
        "Select how many messages to show from history:",
        min_value=1,
        max_value=num_messages,
        value=num_messages,
        step=1,
    )
    # Show last 'num_to_show' messages in order (oldest to newest)
    messages_to_show = st.session_state.messages[-num_to_show:]

    for message in messages_to_show:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.awaiting_image_consent:
        if prompt.strip().lower() in {"yes", "yeah", "ok", "okay", "sure", "yup"}:
            st.markdown("### Related Images and Their Explanations")  # Removed 🖼️
            for path, context in zip(
                st.session_state.pending_image_paths,
                st.session_state.pending_image_contexts,
            ):
                st.image(path, caption=os.path.basename(path))
                st.markdown(f"**Explanation:** {context}")
        else:
            st.markdown("Got it! No images will be shown.")  # Removed ✅

        # Reset image-related states
        st.session_state.awaiting_image_consent = False
        st.session_state.pending_image_paths = []
        st.session_state.pending_image_contexts = []

    else:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response, image_paths, image_contexts = handle_user_input(prompt)
            placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

        if image_paths:
            ask = f"Would you like me to show you the related images from this context? ({len(image_paths)} available)"
            st.session_state.messages.append({"role": "assistant", "content": ask})
            with st.chat_message("assistant"):
                st.markdown(ask)
            st.session_state.awaiting_image_consent = True
            st.session_state.pending_image_paths = image_paths
            st.session_state.pending_image_contexts = image_contexts

# Sidebar for PDF upload
with st.sidebar:
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        st.session_state.uploaded_files.append(uploaded_file)
        process_pdf(uploaded_file)
        st.success(f"Uploaded: {uploaded_file.name}")
