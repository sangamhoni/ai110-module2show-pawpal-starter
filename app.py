import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    "Plan your pets' care for today. Add your pets and their tasks, mark tasks done, "
    "and generate a schedule that fits your time, puts important tasks first, "
    "and warns you about overlapping times."
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

scheduler = Scheduler(owner)

if owner.pets:
    # --- Mark a task done (repeating tasks come back automatically) ---
    st.subheader("Mark a task done")
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))
    pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if pending:
        with st.form("complete_task_form"):
            choice = st.selectbox(
                "Task",
                range(len(pending)),
                format_func=lambda i: (
                    f"{pending[i].pet_name}: {pending[i].title} "
                    f"({pending[i].time or 'any time'}, due {pending[i].due_date:%b %d})"
                ),
            )
            if st.form_submit_button("Mark done"):
                task = pending[choice]
                pet = next(pet for pet in owner.pets if pet.name == task.pet_name)
                next_task = pet.complete(task)
                message = f"Marked '{task.title}' done for {pet.name}."
                if next_task is not None:
                    message += f" It repeats {task.frequency}, so the next one is due {next_task.due_date:%a %b %d}."
                st.session_state.flash = message
                st.rerun()
    else:
        st.caption("Nothing left to do.")

    # --- Sorted + filtered task list ---
    st.subheader("All tasks")
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [pet.name for pet in owner.pets])
    with col2:
        status_filter = st.radio("Status", ["To do", "Done", "All"], horizontal=True)
    shown = scheduler.sort_by_time(
        scheduler.filter_tasks(
            pet_name=None if pet_filter == "All pets" else pet_filter,
            completed={"To do": False, "Done": True, "All": None}[status_filter],
        )
    )
    if shown:
        st.table(
            [
                {
                    "Time": task.time or "—",
                    "Task": task.title,
                    "Pet": task.pet_name,
                    "Minutes": task.duration_minutes,
                    "Priority": task.priority,
                    "Repeats": task.frequency,
                    "Due": f"{task.due_date:%b %d}",
                    "Status": "✅ done" if task.completed else "to do",
                }
                for task in shown
            ]
        )
        st.caption(f"Showing {len(shown)} of {len(owner.get_all_tasks())} tasks, sorted by time.")
    elif owner.get_all_tasks():
        st.info("No tasks match these filters.")
    else:
        st.info("No tasks yet.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    plan = scheduler.generate_plan()
    if not plan and not scheduler.skipped_tasks:
        st.info("Nothing is due today. Add tasks, or check back tomorrow for repeating ones.")
    else:
        used = sum(task.duration_minutes for task in plan)
        col1, col2, col3 = st.columns(3)
        col1.metric("Tasks planned", len(plan))
        col2.metric("Minutes used", f"{used} / {owner.available_minutes}")
        col3.metric("Skipped", len(scheduler.skipped_tasks))

        if scheduler.conflicts:
            st.warning(
                f"**{len(scheduler.conflicts)} time conflict(s):** one person can't do these "
                "at the same time. Move one task in each pair to a different time, or do them "
                "back-to-back.\n\n" + "\n".join(f"- {warning}" for warning in scheduler.conflicts),
                icon="⚠️",
            )
        else:
            st.success("No time conflicts. Today's plan fits together.", icon="✅")

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
        if scheduler.skipped_tasks:
            st.info(
                "**Skipped (not enough time left):**\n\n"
                + "\n".join(f"- {task.summary()}" for task in scheduler.skipped_tasks)
            )
        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan())
