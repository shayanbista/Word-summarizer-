import openai
import streamlit as st
from agent import handle_user_input
import os

# st.title("Your research paper assistant")

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "uploaded_files" not in st.session_state:
#     st.session_state.uploaded_files = []

# if "awaiting_image_consent" not in st.session_state:
#     st.session_state.awaiting_image_consent = False

# if "pending_image_paths" not in st.session_state:
#     st.session_state.pending_image_paths = []

# # Display chat history
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Handle user input
# if prompt := st.chat_input("What is up?"):
#     # Add user message
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # If waiting for image consent
#     if st.session_state.awaiting_image_consent:
#         if prompt.strip().lower() in ["yes", "yeah", "ok", "okay", "sure", "yup"]:
#             st.markdown("### 🖼️ Related Images")
#             for path in st.session_state.pending_image_paths:
#                 st.image(path, caption=os.path.basename(path))
#         else:
#             st.markdown("✅ Got it! No images will be shown.")

#         # Reset image-related states
#         st.session_state.awaiting_image_consent = False
#         st.session_state.pending_image_paths = []

#     else:
#         # Get assistant response and detected image paths
#         with st.chat_message("assistant"):
#             message_placeholder = st.empty()
#             full_response, image_paths = handle_user_input(prompt)
#             message_placeholder.markdown(full_response)

#         # Store assistant response
#         st.session_state.messages.append({"role": "assistant", "content": full_response})

#         # Ask if user wants to see images
#         if image_paths:
#             ask_msg = f"Would you like me to show you the related images from this context? ({len(image_paths)} available)"
#             st.session_state.messages.append({"role": "assistant", "content": ask_msg})
#             with st.chat_message("assistant"):
#                 st.markdown(ask_msg)
#             st.session_state.awaiting_image_consent = True
#             st.session_state.pending_image_paths = image_paths

# # Sidebar for PDF upload
# with st.sidebar:
#     uploaded_file = st.file_uploader("➕ Upload PDF", type="pdf")
#     if uploaded_file is not None:
#         st.session_state.uploaded_files.append(uploaded_file)
#         st.success(f"Uploaded: {uploaded_file.name}")



import openai
import streamlit as st
from agent import handle_user_input
import os



st.title("Your research paper assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "awaiting_image_consent" not in st.session_state:
    st.session_state.awaiting_image_consent = False

if "pending_image_paths" not in st.session_state:
    st.session_state.pending_image_paths = []

if "pending_image_contexts" not in st.session_state:
    st.session_state.pending_image_contexts = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What is up?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # If waiting for image consent
    if st.session_state.awaiting_image_consent:
        if prompt.strip().lower() in ["yes", "yeah", "ok", "okay", "sure", "yup"]:
            st.markdown("### 🖼️ Related Images and Their Explanations")
            for path, context_text in zip(st.session_state.pending_image_paths, st.session_state.pending_image_contexts):
                st.image(path, caption=os.path.basename(path))
                st.markdown(f"**Explanation:** {context_text}")
        else:
            st.markdown("✅ Got it! No images will be shown.")

        # Reset image-related states
        st.session_state.awaiting_image_consent = False
        st.session_state.pending_image_paths = []
        st.session_state.pending_image_contexts = []

    else:
        # Get assistant response, image paths and image contexts
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response, image_paths, image_contexts = handle_user_input(prompt)
            message_placeholder.markdown(full_response)

        # Store assistant response
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Ask if user wants to see images
        if image_paths:
            ask_msg = f"Would you like me to show you the related images from this context? ({len(image_paths)} available)"
            st.session_state.messages.append({"role": "assistant", "content": ask_msg})
            with st.chat_message("assistant"):
                st.markdown(ask_msg)
            st.session_state.awaiting_image_consent = True
            st.session_state.pending_image_paths = image_paths
            st.session_state.pending_image_contexts = image_contexts

# Sidebar for PDF upload
with st.sidebar:
    uploaded_file = st.file_uploader("➕ Upload PDF", type="pdf")
    if uploaded_file is not None:
        st.session_state.uploaded_files.append(uploaded_file)
        st.success(f"Uploaded: {uploaded_file.name}")
