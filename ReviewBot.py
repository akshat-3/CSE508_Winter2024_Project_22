import streamlit as st
import openai
# openai.api_key = ''
class ReviewChatbot:
    def __init__(self, reviews, chat_history=[]):
        self.reviews = reviews
        self.chat_history = chat_history
        self.system_prompt = "You are a helpful assistant that summarizes and answers questions about product reviews."

    def get_contents(self, message, role):
        return [{"role": role, "content": content} for content in message]

    def chat(self, message):
        messages = self.get_contents(self.reviews, "user")
        for chat in self.chat_history:
            messages.append({"role": chat["role"], "content": chat["content"]})
        messages.append({"role": "user", "content": message})
        

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                *messages,
            ],
            max_tokens=150,
            temperature=0.7,
        )

        return response.choices[0].message['content']


st.markdown('### Group 22 IR Project')
st.markdown('#### E-Commerce Competitive Analysis System')
st.markdown('Review Analysis by ReviewBot')
params = st.query_params['param']
# param = params['param'] if 'param' in params else ' '
st.markdown(f'Ask a question about your product: {params}')

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = [] 
f = open("reviews.txt", "r", encoding='utf-8')
reviews = f.read()
reviews = reviews.split('\n')
f.close()
messages = st.container(height=600)
flag = 0
if not st.session_state['chat_history']:
    messages.chat_message("assistant").write("Hi! I'm ReviewBot. I'm here to help you with your product reviews.")
    flag = 1
for message in st.session_state['chat_history']:
    messages.chat_message(message["role"]).write(message["content"])
# st.session_state['chat_history'].clear()
if flag == 1:
    st.session_state['chat_history'].append({"role": "assistant", "content": "Hi! I'm ReviewBot. I'm here to help you with your product reviews."})

if prompt := st.chat_input("Say something"):
    chatbot = ReviewChatbot(reviews, st.session_state['chat_history'])
    messages.chat_message("user").write(prompt)
    try:
        answer = chatbot.chat(prompt)
    except:
        answer = "I'm sorry, I don't have an answer to that question."
    messages.chat_message("assistant").write(f"{answer}")
    st.session_state['chat_history'].append({"role": "user", "content": prompt})
    st.session_state['chat_history'].append({"role": "assistant", "content": answer})
