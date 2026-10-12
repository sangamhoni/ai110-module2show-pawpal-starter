import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Keep one Owner in session_state so pets and tasks survive Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=60)
owner = st.session_state.owner

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value="Jordan", key="owner_name")
with col2:
    owner.available_minutes = int(
        st.number_input(
            "Minutes available today", min_value=0, max_value=1440, value=60, step=5,
            key="available_minutes",
        )
    )

st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Enter a pet name.")
        else:
            try:
                owner.add_pet(Pet(pet_name.strip(), species))
                st.success(f"Added {pet_name.strip()}.")
            except ValueError as error:
                st.error(str(error))

if owner.pets:
    st.table([{"Pet": pet.name, "Species": pet.species} for pet in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.subheader("Tasks")
if not owner.pets:
    st.caption("Add a pet before adding tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [pet.name for pet in owner.pets])
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        col4, col5 = st.columns(2)
        with col4:
            task_time = st.text_input("Time (HH:MM, optional)", value="")
        with col5:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        if st.form_submit_button("Add task"):
            pet = next(pet for pet in owner.pets if pet.name == pet_choice)
            try:
                pet.add_task(
                    Task(task_title.strip(), int(duration), priority,
                         time=task_time.strip(), frequency=frequency)
                )
                st.success(f"Added '{task_title.strip()}' for {pet.name}.")
            except ValueError as error:
                st.error(str(error))

tasks = owner.get_all_tasks()
if tasks:
    st.table(
        [
            {
                "Pet": task.pet_name,
                "Task": task.title,
                "Time": task.time or "—",
                "Minutes": task.duration_minutes,
                "Priority": task.priority,
                "Frequency": task.frequency,
            }
            for task in tasks
        ]
    )
else:
    st.info("No tasks yet.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    if plan:
        st.table(
            [
                {
                    "Time": task.time or "—",
                    "Task": task.title,
                    "Pet": task.pet_name,
                    "Minutes": task.duration_minutes,
                    "Priority": task.priority,
                }
                for task in scheduler.sort_by_time(plan)
            ]
        )
    for warning in scheduler.conflicts:
        st.warning(warning)
    st.text(scheduler.explain_plan())
