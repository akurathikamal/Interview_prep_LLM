import streamlit as st
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import streamlit as st
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]


# Supported languages
languages = ["Python", "Java", "C++"]

# Streamlit UI
st.title("🧠 Interview Q&A + Coding Challenge Generator (Groq LLM)")
job_title = st.text_input("Enter a job title or skill (e.g., Data Analyst, SQL)")
difficulty = st.selectbox("Select difficulty level", ["Easy", "Medium", "Hard"])
num_questions = st.slider("Number of interview questions", 3, 10, 5)
language = st.selectbox("Choose programming language for coding challenge", languages)

# Generate button
if st.button("Generate Questions & Challenge"):
    if not GROQ_API_KEY:
        st.error("API key not found. Please check your .env file.")
    elif not job_title.strip():
        st.warning("Please enter a job title or skill.")
    else:
        # Prompt for Groq LLM
        prompt = f"""
        Generate {num_questions} interview questions for the role or skill: {job_title}.
        Each question should include:
        - A sample answer
        - Difficulty level: {difficulty}
        - One tip for answering well

        Then, generate:
        - 2 multiple-choice questions (MCQs) with 4 options each and indicate the correct answer.
        - 1 coding challenge related to data structures in {language}.
          Include:
          - Problem statement
          - Starter code with missing parts
          - A clean, beginner-friendly solution
          - 2 sample test cases with expected output
        Format everything clearly.
        """

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "moonshotai/kimi-k2-instruct-0905",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]

            # Split content into Q&A and coding challenge
            if "Problem statement:" in content:
                qa_part, coding_part = content.split("Problem statement:", 1)
                st.markdown("### 🎯 Interview Questions + MCQs")
                st.write(qa_part)

                st.markdown("### 🧩 Coding Challenge")
                problem_statement = coding_part.split("Starter code")[0].strip()
                st.write("**Problem statement:** " + problem_statement)

                starter_code = ""
                if "Starter code" in coding_part:
                    starter_code = coding_part.split("Starter code")[1].split("Test cases")[0].strip()

                st.markdown("### 🧪 Starter Code")
                st.code(starter_code, language="python")

                st.markdown("### ✏️ Try Your Own Code")
                user_code = st.text_area("Write your solution here:", value=starter_code, height=300)

                if language == "Python" and st.button("Run Test Cases"):
                    test_code = """
def run_tests():
    try:
        # Example: assume user defines a function called 'reverse_list'
        result1 = reverse_list([1, 2, 3])
        result2 = reverse_list([4, 5])
        assert result1 == [3, 2, 1], f"Test 1 failed: got {result1}"
        assert result2 == [5, 4], f"Test 2 failed: got {result2}"
        print("✅ All test cases passed!")
    except AssertionError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Runtime error: {e}")

run_tests()
"""
                    try:
                        exec(user_code + "\n" + test_code)
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            else:
                st.write(content)  # fallback if structure is different
        else:
            st.error(f"Error {response.status_code}: {response.json()['error']['message']}")
