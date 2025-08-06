import streamlit as st
from crewai import Agent, Task, Crew
from litellm import completion
import os
import time


st.set_page_config(page_title="Remote Diagnostic Assistant", layout="centered")
st.title("🩺 AI Diagnostic Assistant for Remote Areas")
st.write("This app is designed to assist healthcare professionals in remote areas by providing AI-driven diagnostic support.")
st.write("Please fill in the patient details below to get started.")

with st.form("patient_form"):
    symptoms = st.text_area("Symptoms (comma-separated)")
    temp = st.text_input("Body Temperature (°F)")
    bp = st.text_input("Blood Pressure (e.g. 120/80)")
    pulse = st.text_input("Pulse Rate (bpm)")
    labs = st.text_area("Basic Lab Results (e.g. WBC 13000, Hb 10)")
    history = st.text_area("Relevant Medical History (comma-separated)")
    submitted = st.form_submit_button("Run Diagnosis")

if submitted:
    raw_input = f"Symptoms: {symptoms}. Vitals: Temp {temp}°F, BP {bp}, Pulse {pulse}. Labs: {labs}. History: {history}."
    st.success("Patient input collected! Running diagnosis...")
    status_placeholder = st.empty()

    class GeminiLLM:
        def __init__(self, model_name="gemini/gemini-2.0-flash-lite", temperature=0.2):
            self.model_name = model_name
            self.temperature = temperature
            self.api_key = "AIzaSyDKNsjNRiGxtFAxSmnq3SMZ_u50iF_wVAY"

        def run(self, messages):
            response = completion(
                model=self.model_name,
                messages=messages,
                api_key=self.api_key,
                litellm_provider="google",
                temperature=self.temperature
            )
            return response["choices"][0]["message"]["content"]

        def __call__(self, prompt, stop=None):
            messages = [{"role": "user", "content": prompt}]
            return self.run(messages)

    llm = GeminiLLM()

    # Define agents in CrewAI format
    input_collector = Agent(
        name="Input Collector",
        role="Data Organizer",
        goal="Collect and structure raw patient data including symptoms, vitals, labs, and history",
        backstory="You are a meticulous data collector who ensures all patient information is well organized for further processing.",
        allow_delegation=False,
        llm=llm
    )

    preprocessor = Agent(
        name="Preprocessor",
        role="Medical Data Cleaner",
        goal="Clean, normalize, and format patient data for accurate analysis",
        backstory="You are responsible for ensuring data consistency by converting unstructured inputs into a standardized format.",
        allow_delegation=False,
        llm=llm
    )

    symptom_interpreter = Agent(
        name="Symptom Interpreter",
        role="Symptom Analyst",
        goal="Identify probable conditions from symptoms",
        backstory="You are a clinical analyst trained to spot disease patterns based on symptom clusters.",
        allow_delegation=False,
        llm=llm
    )

    vital_sign_analyzer = Agent(
        name="Vital Sign Analyzer",
        role="Vital Sign Specialist",
        goal="Assess vital signs for abnormalities and potential risks",
        backstory="You are a specialist who understands the implications of abnormal vital signs in medical diagnostics.",
        allow_delegation=False,
        llm=llm
    )

    lab_result_analyzer = Agent(
        name="Lab Result Analyzer",
        role="Lab Analyst",
        goal="Interpret basic lab results and associate them with potential medical conditions",
        backstory="You are an expert in evaluating laboratory data and identifying significant markers.",
        allow_delegation=False,
        llm=llm
    )

    history_analyzer = Agent(
        name="Medical History Analyzer",
        role="Historical Context Analyst",
        goal="Analyze medical history to provide context for diagnosis",
        backstory="You explore the patient's past health records to assess risks and chronic issues that may impact current symptoms.",
        allow_delegation=False,
        llm=llm
    )

    diagnostic_synthesizer = Agent(
        name="Diagnostic Synthesizer",
        role="Diagnosis Integrator",
        goal="Combine all analytical outputs to deliver a comprehensive differential diagnosis",
        backstory="You are a master diagnostician who consolidates all aspects of patient data into a cohesive diagnostic view.",
        allow_delegation=True,
        llm=llm
    )

    recommendation_agent = Agent(
        name="Recommendation Agent",
        role="Follow-Up Advisor",
        goal="Recommend appropriate diagnostic tests or treatments",
        backstory="You advise next steps in the clinical workflow based on preliminary diagnostic conclusions.",
        allow_delegation=False,
        llm=llm
    )

    explanation_agent = Agent(
        name="Explanation Agent",
        role="Clinical Communicator",
        goal="Explain the diagnostic process and reasoning in human-friendly language",
        backstory="You are skilled at translating complex medical logic into clear explanations for non-specialists.",
        allow_delegation=False,
        llm=llm
    )

    # Define tasks in CrewAI format
    collect_task = Task(
        description=f"Organize this raw patient input: {raw_input}",
        expected_output="Structured JSON format of patient information",
        agent=input_collector
    )

    preprocess_task = Task(
        description="Clean and normalize the structured input for consistent format.",
        expected_output="Standardized patient data in clean JSON format",
        agent=preprocessor,
        context=[collect_task]
    )

    symptom_task = Task(
        description="Analyze the symptoms and suggest potential diagnoses based on symptom clusters.",
        expected_output="List of probable conditions derived from symptoms",
        agent=symptom_interpreter,
        context=[preprocess_task]
    )

    vitals_task = Task(
        description="Evaluate vital signs for abnormal values and their potential clinical meanings.",
        expected_output="Abnormalities in vitals and possible related conditions",
        agent=vital_sign_analyzer,
        context=[preprocess_task]
    )

    labs_task = Task(
        description="Analyze basic lab results to highlight abnormal findings and suggest causes.",
        expected_output="Interpretation of lab values and related potential issues",
        agent=lab_result_analyzer,
        context=[preprocess_task]
    )

    history_task = Task(
        description="Examine patient medical history for risk factors, chronic conditions, or past relevant events.",
        expected_output="Insightful context derived from medical history",
        agent=history_analyzer,
        context=[preprocess_task]
    )

    diagnosis_task = Task(
        description="Integrate all previous outputs to generate a differential diagnosis.",
        expected_output="Top 2-3 likely diagnoses with reasoning",
        agent=diagnostic_synthesizer,
        context=[symptom_task, vitals_task, labs_task, history_task]
    )

    recommendation_task = Task(
        description="Based on the diagnosis, recommend follow-up tests or treatments.",
        expected_output="List of recommended diagnostics or treatment plans",
        agent=recommendation_agent,
        context=[diagnosis_task]
    )

    explanation_task = Task(
        description="Summarize the diagnostic process and conclusions in layman's terms.",
        expected_output="Clear explanation of diagnostic path for clinicians or patients",
        agent=explanation_agent,
        context=[diagnosis_task]
    )

    crew = Crew(
        agents=[input_collector, preprocessor, symptom_interpreter, vital_sign_analyzer,
                lab_result_analyzer, history_analyzer, diagnostic_synthesizer,
                recommendation_agent, explanation_agent],
        tasks=[collect_task, preprocess_task, symptom_task, vitals_task, labs_task,
               history_task, diagnosis_task, recommendation_task, explanation_task],
        verbose=True
    )

    result = crew.kickoff()

    agent_list = [
        "Input Collector Expert is parsing the patients details...",
        "Preprocessor Expert is analysing the patients details...",
        "Symptom Interpreter Expert is analysing the Patients Symptoms...",
        "Vital Sign Specailist is detecting Abnormalities and risks...",
        "Lab Analyst is interpreting thr lab results..."
        "Medical history of the Patient is being interpreted..."
        "Diagnostian is generating the summary of the Patient...",
        "Recommendation Agent is recommending further tests...",
        "Explanation Agent is generating the final summary of the Patient...",
    ]

    for agent_msg in agent_list:
        status_placeholder.info(f"🔎 {agent_msg}")
        time.sleep(1.5) 

    status_placeholder.success("✅ All tasks completed! Here’s your Diagnostic Summary:")

    filename = f"Diagnostic_summary.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(result))

    final_output = str(result)
    if final_output.strip().startswith("```") and final_output.strip().endswith("```"):
        final_output = final_output.strip().lstrip("```").rstrip("```").strip()

    st.subheader("📄 Final Diagnostic Summary")
    st.markdown(final_output, unsafe_allow_html=True)

    with open(filename, "rb") as f:
        st.download_button(
            label="📥 Download Diagnostic Summary",
            data=f,
            file_name=filename,
            mime="text/plain"
        )
