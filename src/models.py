from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class File(BaseModel):
    path: str = Field(description="Path of the file to be created or modified")
    purpose: str = Field(description="Purpose of the file. E.g. 'main app logic', 'styles for the app' etc.")

class Plan(BaseModel):
    name: str = Field(description="The name of the app to be built")
    description: str = Field(description="A short description of the app to be built")
    tech_stack: str = Field(description="The tech stack to be used for the app. E.g. - 'JS', 'Python' etc.")
    features: list[str] = Field(description="A list of features the app should have.")
    files: list[File] = Field(description="A list of files to be created, each with 'path' and 'purpose'.")

class ImplementationTask(BaseModel):
    filepath: str = Field(description="The path to the file to be modified")
    task_description: str = Field(description="A detailed description of the task to be performed on the file, e.g. 'add user authentication', 'implement data processing logic', etc.")

class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(description="A list of steps to be taken to implement the task")
    model_config = ConfigDict(extra="allow")

class CoderState(BaseModel):
    task_plan: TaskPlan = Field(description="The plan for the task to be implemented")
    current_step_idx: int = Field(0, description="The index of the current step in the implementation steps")
    current_file_content: Optional[str] = Field(None, description="The content of the file currently being edited or created")