import streamlit as st
from langchain_core.prompts import PromptTemplate
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

# Prompt templates
plan_prompt_template = """
You are a fitness and diet planner. Using these inputs, create two detailed plans:
1. A **workout plan** table listing day-to-day exercises for {number_of_weeks} weeks.
2. A **diet plan** table listing day-to-day food intake for {number_of_weeks} weeks.

Inputs:
- Workout type: {workout_type}
- Diet type: {diet_type}
- Current body weight: {current_weight} kg
- Target weight: {target_weight} kg
- Specific dietary restrictions: {dietary_restrictions}
- Health conditions: {health_conditions}
- Age: {age}
- Gender: {gender}
- Other instructions: {comments}

Return the plans in a neat, structured format with detailed descriptions and tables, and include any relevant key notes.
"""

chat_prompt_template = """
You are a fitness and diet expert. Answer the following user question based on the given plan:

Plan: {plan}

Question: {question}

Provide a clear and helpful response.
"""

plan_prompt = PromptTemplate(
    input_variables=[
        "workout_type", "diet_type", "current_weight", "target_weight",
        "dietary_restrictions", "health_conditions", "age", "gender",
        "number_of_weeks", "comments",
    ],
    template=plan_prompt_template,
)

chat_prompt = PromptTemplate(
    input_variables=["plan", "question"],
    template=chat_prompt_template,
)

def generate_plan(inputs: dict) -> str:
    prompt_str = plan_prompt.format(**inputs)
    messages = [{"role": "user", "content": prompt_str}]
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        temperature=1,
        max_completion_tokens=3072,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content

def answer_question(inputs: dict) -> str:
    prompt_str = chat_prompt.format(**inputs)
    messages = [{"role": "user", "content": prompt_str}]
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content

# ✅ CSS loader with fallback if file is missing
def local_css(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ style.css not found! Please add it to the project folder.")

# ✅ Export to text file
def export_plan(plan_text):
    with open("your_fitness_plan.txt", "w", encoding="utf-8") as f:
        f.write(plan_text)

# ✅ Page setup
st.set_page_config(page_title="🏋️ Fitness & Diet AI Planner", layout="wide")

# ✅ Load the auto-detect theme CSS
local_css("style.css")

# ✅ Title
st.title("✨🏋️ Personalized Fitness & Diet Planner 💪🍎")

col1, col2 = st.columns(2)

with col1:
    st.header("🎯 Enter Your Goals")
    workout_type = st.text_input("🏋️ Workout Type (e.g., Fat Loss, Bulking)")
    diet_type = st.text_input("🥗 Diet Type (e.g., Keto, Mediterranean)")
    current_weight = st.number_input("⚖️ Current Weight (kg)", 30.0, 200.0, 75.0)
    target_weight = st.number_input("🎯 Target Weight (kg)", 30.0, 200.0, 70.0)
    dietary_restrictions = st.text_input("🚫 Dietary Restrictions (e.g., No gluten)")
    health_conditions = st.text_input("❤️ Health Conditions (e.g., Asthma)")
    age = st.number_input("🎂 Age", 10, 100, 30)
    gender = st.selectbox("👤 Gender", ["Male", "Female", "Other"])
    number_of_weeks = st.slider("📅 Plan Duration (weeks)", 1, 12, 4)
    comments = st.text_area("📝 Any other instructions")

    if st.button("🚀 Generate My Plan"):
        st.session_state.messages = []
        with st.spinner("🤖 AI is generating your plan..."):
            try:
                plan = generate_plan({
                    "workout_type": workout_type,
                    "diet_type": diet_type,
                    "current_weight": current_weight,
                    "target_weight": target_weight,
                    "dietary_restrictions": dietary_restrictions,
                    "health_conditions": health_conditions,
                    "age": age,
                    "gender": gender,
                    "number_of_weeks": number_of_weeks,
                    "comments": comments,
                })
                st.session_state.plan = plan
                st.success("✅ Your personalized plan is ready!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

with col2:
    if "plan" in st.session_state and st.session_state.plan:
        st.header("📋 Your Generated Plan")
        st.markdown(
            f'<div class="plan-box">{st.session_state.plan}</div>',
            unsafe_allow_html=True
        )
        st.download_button("📥 Download Plan", st.session_state.plan, file_name="Your_Fitness_Plan.txt")

# ✅ Chat with AI
if "plan" in st.session_state and st.session_state.plan:
    st.markdown("---")
    st.subheader("💬 Ask me anything about your plan!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your plan here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("✍️ AI is typing..."):
            try:
                reply = answer_question({
                    "plan": st.session_state.plan,
                    "question": prompt,
                })
            except Exception as e:
                reply = f"❌ Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").markdown(reply)

st.markdown("---")
st.caption("🔋🤗✨")
