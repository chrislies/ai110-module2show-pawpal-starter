import streamlit as st

from pawpal_system import CareTask, Owner, Pet, Scheduler

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

# st.session_state survives reruns, so only create the Owner the first time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
owner = st.session_state.owner

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
available = st.number_input(
    "Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes or 60
)
owner.name = owner_name
owner.set_available_minutes(int(available))

st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Pet name is required.")
        elif any(p.name == pet_name.strip() for p in owner.pets):
            st.error(f"You already have a pet named {pet_name.strip()}.")
        else:
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name.strip()}!")

if owner.pets:
    st.write("Your pets:")
    st.table([{"name": p.name, "species": p.species, "tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

scheduler = Scheduler(owner)

st.markdown("### Tasks")
if owner.pets:
    target_name = st.selectbox("Pet", [p.name for p in owner.pets])
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    col4, col5 = st.columns(2)
    with col4:
        preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")
    with col5:
        recurring = st.selectbox("Repeats", ["once", "daily", "weekly"])

    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == target_name)
        try:
            pet.add_task(
                CareTask(
                    task_title,
                    int(duration),
                    priority,
                    preferred_time=preferred_time.strip() or None,
                    recurring=None if recurring == "once" else recurring,
                )
            )
            st.success(f"Added '{task_title}' for {pet.name}.")
        except ValueError:
            st.error("Preferred time must look like HH:MM, for example 08:30.")

    # Conflicts are shown as soon as they exist, so the owner can fix them
    # before generating a schedule.
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning(
            f"**{len(conflicts)} scheduling conflict(s) found.** Move one task in "
            "each pair to a different time, or shorten it, so they no longer overlap."
        )
        for message in conflicts:
            st.warning(message.removeprefix("Warning: "), icon="⚠️")

    st.markdown("#### Your tasks")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with filter_col2:
        status_filter = st.selectbox("Show status", ["All", "Pending", "Completed"])

    shown = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    )
    shown = scheduler.sort_by_time(shown)  # earliest preferred time first
    if shown:
        st.caption("Sorted by preferred time; tasks without a time are listed last.")
        st.table(
            [
                {
                    "Time": t.preferred_time or "—",
                    "Pet": t.pet.name,
                    "Task": t.title,
                    "Minutes": t.duration_minutes,
                    "Priority": t.priority,
                    "Repeats": t.recurring or "once",
                    "Due": t.due_date.isoformat(),
                    "Status": "Done" if t.completed else "Pending",
                }
                for t in shown
            ]
        )
    else:
        st.info("No tasks match these filters. Add a task above or change the filters.")

    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))

    pending = scheduler.filter_tasks(completed=False)
    if pending:
        to_complete = st.selectbox(
            "Mark a task complete",
            range(len(pending)),
            format_func=lambda i: f"{pending[i].pet.name}: {pending[i].title}",
        )
        if st.button("Mark complete"):
            task = pending[to_complete]
            following = scheduler.mark_task_complete(task)
            if following:
                st.session_state.flash = (
                    f"Done! '{task.title}' repeats {task.recurring}; the next one is due "
                    f"{following.due_date.isoformat()}."
                )
            else:
                st.session_state.flash = f"Done! '{task.title}' is complete."
            st.rerun()  # redraw the tables above with the new state
else:
    st.info("Add a pet before adding tasks.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    plan = scheduler.build_plan()
    if plan:
        st.success(f"Plan ready: {scheduler.summary()}")
        st.table(
            [
                {
                    "Start": start,
                    "Pet": task.pet.name,
                    "Task": task.title,
                    "Minutes": task.duration_minutes,
                    "Priority": task.priority,
                }
                for task, start in plan
            ]
        )
    else:
        st.warning("Nothing could be scheduled. Add tasks or more available time.")
    if scheduler.skipped:
        st.warning(
            "Not enough time for: "
            + ", ".join(f"{t.pet.name}'s {t.title}" for t, _ in scheduler.skipped)
            + ". Increase the minutes available or lower their priority."
        )
    with st.expander("Why this plan?"):
        st.text(scheduler.explain())
