from dotenv import load_dotenv
from langchain.agents import create_agent

from src.tools import read_file, write_file, list_files, get_current_directory

load_dotenv()

from langchain_groq import ChatGroq

from src.models import Plan, TaskPlan, CoderState
from src.prompts import planner_prompt, architect_prompt, coder_prompt
from utils.constants import LLM_MODEL

llm = ChatGroq(model=LLM_MODEL)

def planner_agent(state: dict) -> dict:
    user_prompt = state["user_prompt"]
    llm_prompt = planner_prompt(user_prompt)
    res = llm.with_structured_output(Plan).invoke(llm_prompt)

    if res is None:
        raise ValueError("Planner agent didn't return a valid response")

    return {"plan": res}


def architect_agent(state: dict) -> dict:
    plan: Plan = state["plan"]
    llm_prompt = architect_prompt(plan.model_dump_json())
    resp = llm.with_structured_output(TaskPlan).invoke(llm_prompt)
    if resp is None:
        raise ValueError("Architect agent didn't return a valid response.")

    resp.plan = plan    # Carry forward the 'plan' (output state) from previous agent to the next
    return {"task_plan": resp}

def coder_agent(state: dict) -> dict:
    coder_state = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(
            task_plan=state["task_plan"],
            current_step_idx=0,
            current_file_content=None,
        )

    implementation_steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(implementation_steps):
        return {"coder_state": coder_state, "status": "DONE"}

    current_task = implementation_steps[coder_state.current_step_idx]
    existing_file_content = read_file.run(current_task.filepath)

    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content: {existing_file_content}\n"
        "Use write_file(path, content) to save your changes."
    )
    coder_tools = [read_file, write_file, list_files, get_current_directory]

    agent = create_agent(llm, coder_tools)

    agent.invoke({
        "messages": [
            {"role": "system", "content": coder_prompt()},
            {"role": "user", "content": user_prompt}
        ]
    })

    coder_state.current_step_idx += 1
    return {"coder_state": coder_state}