# import os
# import streamlit as st
# from agent import handle_user_input
# from pdf_processor import process_pdf

# st.title("Your Research Paper Assistant")


# st.session_state.setdefault("messages", [])
# st.session_state.setdefault("uploaded_files", [])
# st.session_state.setdefault("awaiting_image_consent", False)
# st.session_state.setdefault("pending_image_paths", [])
# st.session_state.setdefault("pending_image_contexts", [])


# if st.session_state.messages:
#     num_messages = len(st.session_state.messages)
#     num_to_show = st.slider(
#         "Select how many messages to show from history:",
#         min_value=1,
#         max_value=num_messages,
#         value=num_messages,
#         step=1,
#     )

#     messages_to_show = st.session_state.messages[-num_to_show:]

#     for message in messages_to_show:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])


# if prompt := st.chat_input("What is up?"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     if st.session_state.awaiting_image_consent:
#         if prompt.strip().lower() in {"yes", "yeah", "ok", "okay", "sure", "yup"}:
#             st.markdown("### Related Images and Their Explanations")
#             for path, context in zip(
#                 st.session_state.pending_image_paths,
#                 st.session_state.pending_image_contexts,
#             ):
#                 st.image(path, caption=os.path.basename(path))
#                 st.markdown(f"**Explanation:** {context}")
#         else:
#             st.markdown("Got it! No images will be shown.")

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
#             print("image paths appended", image_paths)
#             st.session_state.pending_image_contexts = image_contexts

# with st.sidebar:
#     uploaded_file = st.file_uploader("Upload PDF", type="pdf")
#     if uploaded_file:
#         with st.spinner(f"Processing {uploaded_file.name}..."):
#             st.session_state.uploaded_files.append(uploaded_file)
#             process_pdf(uploaded_file)
#         st.success(f"Uploaded: {uploaded_file.name}")


# import os
# import hashlib
# import streamlit as st
# from agent import handle_user_input
# from pdfProcessor import process_pdf

# st.title("Your Research Paper Assistant")

# st.session_state.setdefault("messages", [])
# st.session_state.setdefault("uploaded_files", [])
# st.session_state.setdefault(
#     "processed_file_hashes", set()
# )  # Track processed file hashes
# st.session_state.setdefault("awaiting_image_consent", False)
# st.session_state.setdefault("pending_image_paths", [])
# st.session_state.setdefault("pending_image_contexts", [])


# def get_file_hash(uploaded_file):
#     """Generate a hash for the uploaded file to uniquely identify it."""
#     uploaded_file.seek(0)  # Reset file pointer
#     file_hash = hashlib.md5(uploaded_file.read()).hexdigest()
#     uploaded_file.seek(0)  # Reset file pointer again
#     return file_hash


# if st.session_state.messages:
#     num_messages = len(st.session_state.messages)
#     num_to_show = st.slider(
#         "Select how many messages to show from history:",
#         min_value=1,
#         max_value=num_messages,
#         value=num_messages,
#         step=1,
#     )

#     messages_to_show = st.session_state.messages[-num_to_show:]

#     for message in messages_to_show:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

# if prompt := st.chat_input("What is up?"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     if st.session_state.awaiting_image_consent:
#         if prompt.strip().lower() in {"yes", "yeah", "ok", "okay", "sure", "yup"}:
#             st.markdown("### Related Images and Their Explanations")
#             for path, context in zip(
#                 st.session_state.pending_image_paths,
#                 st.session_state.pending_image_contexts,
#             ):
#                 st.image(path, caption=os.path.basename(path))
#                 st.markdown(f"**Explanation:** {context}")
#         else:
#             st.markdown("Got it! No images will be shown.")

#         st.session_state.awaiting_image_consent = False
#         st.session_state.pending_image_paths = []
#         st.session_state.pending_image_contexts = []

#     else:
#         with st.chat_message("assistant"):
#             placeholder = st.empty()
#             print("handle_user_input response:", handle_user_input(prompt))
#             full_response, image_paths, image_contexts = handle_user_input(prompt)
#             print("image fetch from stramlit",image_paths)
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
#             print("image paths appended", image_paths)
#             st.session_state.pending_image_contexts = image_contexts

# with st.sidebar:
#     uploaded_file = st.file_uploader("Upload PDF", type="pdf")
#     if uploaded_file:
#         file_hash = get_file_hash(uploaded_file)

#         if file_hash not in st.session_state.processed_file_hashes:
#             with st.spinner(f"Processing {uploaded_file.name}..."):
#                 st.session_state.uploaded_files.append(uploaded_file)
#                 process_pdf(uploaded_file)
#                 st.session_state.processed_file_hashes.add(file_hash)
#             st.success(f"Uploaded: {uploaded_file.name}")
#         else:
#             st.success(f"Already processed: {uploaded_file.name}")


import os
import hashlib
import streamlit as st
from agent import handle_user_input
from pdfProcessor import process_pdf

st.title("Your Research Paper Assistant")

st.session_state.setdefault("messages", [])
st.session_state.setdefault("uploaded_files", [])
st.session_state.setdefault(
    "processed_file_hashes", set()
)  # Track processed file hashes
st.session_state.setdefault("awaiting_image_consent", False)
st.session_state.setdefault("pending_image_paths", [])
st.session_state.setdefault("pending_image_contexts", [])


def get_file_hash(uploaded_file):
    """Generate a hash for the uploaded file to uniquely identify it."""
    uploaded_file.seek(0)  # Reset file pointer
    file_hash = hashlib.md5(uploaded_file.read()).hexdigest()
    uploaded_file.seek(0)  # Reset file pointer again
    return file_hash


if st.session_state.messages:
    num_messages = len(st.session_state.messages)
    num_to_show = st.slider(
        "Select how many messages to show from history:",
        min_value=1,
        max_value=num_messages,
        value=num_messages,
        step=1,
    )

    messages_to_show = st.session_state.messages[-num_to_show:]

    for message in messages_to_show:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.awaiting_image_consent:
        if prompt.strip().lower() in {"yes", "yeah", "ok", "okay", "sure", "yup"}:
            st.markdown("### Related Images and Their Explanations")
            for path, context in zip(
                st.session_state.pending_image_paths,
                st.session_state.pending_image_contexts,
            ):
                st.image(path, caption=os.path.basename(path))
                st.markdown(f"**Explanation:** {context}")
        else:
            st.markdown("Got it! No images will be shown.")

        st.session_state.awaiting_image_consent = False
        st.session_state.pending_image_paths = []
        st.session_state.pending_image_contexts = []

    else:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response, image_paths, image_contexts = handle_user_input(prompt)
            print(
                "handle_user_input response:",
                (full_response, image_paths, image_contexts),
            )

            # Debug to ensure all image paths exist
            for path in image_paths:
                if not os.path.exists(path):
                    print(f"Warning: Missing image file -> {path}")

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
            print("image paths appended", image_paths)
            st.session_state.pending_image_contexts = image_contexts

with st.sidebar:
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        file_hash = get_file_hash(uploaded_file)

        if file_hash not in st.session_state.processed_file_hashes:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                st.session_state.uploaded_files.append(uploaded_file)
                process_pdf(uploaded_file)
                st.session_state.processed_file_hashes.add(file_hash)
            st.success(f"Uploaded: {uploaded_file.name}")
        else:
            st.success(f"Already processed: {uploaded_file.name}")
