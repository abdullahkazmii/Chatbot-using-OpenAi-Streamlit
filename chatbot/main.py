from openai import OpenAI
import streamlit as st

# Initialize OpenAI client with API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("ChatGPT Clone")

# Set default model if not in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Display assistant's welcome message
with st.chat_message("assistant"):
    st.write("Hey there! I'm a chatbot. How can I help you today?")

# Initialize message history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Get user input
if prompt := st.chat_input("What's up?"):
    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    # Create a placeholder for the assistant's response
    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        full_response = ''

        try:
            # Stream the OpenAI API response
            response_stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {'role': m['role'], 'content': m['content']}
                    for m in st.session_state.messages
                ],
                stream=True
            )

            # Process the response
            for response in response_stream:
                # Access the `choices` directly and process the `delta.content`
                for choice in response.choices:
                    content = getattr(choice.delta, "content", None)
                    if content:  # Ensure content is not None before concatenating
                        full_response += content
                        message_placeholder.markdown(full_response)

            # Store the full response and display it
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.write("Debugging Error:", str(e))
