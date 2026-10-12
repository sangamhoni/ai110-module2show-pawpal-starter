# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

These are the three main things a user should be able to do in PawPal+:

1. **Add their pet and their own info.** The user types in their name, their pet's name, and what kind of animal it is. They can also say how much time they have for pet care each day. This way the app knows who it is planning for.

2. **Add and edit care tasks.** The user can add the things their pet needs, like a walk, feeding, medicine, playtime, or grooming. For each task, they say how long it takes and how important it is (high, medium, or low). They can also change or remove a task later.

3. **See today's plan.** The user clicks a button and the app makes a plan for the day. It puts the most important tasks first and fits them into the time the owner has. The app also explains why it picked this order, and which tasks it skipped if there wasn't enough time.

**a. Initial design**

My design has four classes:

- **Owner** stores the owner's name, how many minutes they have for pet care each day, and their list of pets. It can add or remove a pet and give back all the tasks from every pet.
- **Pet** stores the pet's name, its species, and its list of care tasks. It can add, edit, and remove tasks.
- **Task** is one care activity, like a walk or a feeding. It stores the title, how long it takes, its priority (low, medium, or high), and whether it is done. It can turn its priority into a number for sorting and mark itself complete.
- **Scheduler** makes the daily plan. It gets the owner's tasks, sorts them by priority, and adds them until the owner's time runs out. It keeps a list of planned tasks and a list of skipped tasks so it can explain the plan.

An owner has many pets, a pet has many tasks, and the scheduler plans for one owner. I used dataclasses for Owner, Pet, and Task because they mostly hold data.

**b. Design changes**

Yes. After I asked AI to review my skeleton, I made three changes:

1. **Added `pet_name` to Task.** When the owner's tasks are combined into one list, the scheduler couldn't tell which pet each task was for. Now `Pet.add_task()` saves the pet's name on the task, so the plan can say "Walk (Mochi)".
2. **Added a `PRIORITY_RANKS` table and a validation step for Task.** Priority was just text, so a typo like "High" or "urgent" would break sorting. Now there is one place that lists the allowed priorities, and Task will check its priority and duration when it is created.
3. **Made the `generate_plan()` rules clearer.** It will clear old results before planning and skip tasks that are already done, so running it twice won't double the plan.

I did not change the greedy approach (most important tasks first). It is simple and easy to explain, even though a long high-priority task can sometimes push out several shorter ones.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers five things:
1. **Time available:** the owner's minutes for the day. This is a hard limit, so a task that doesn't fit is skipped.
2. **Priority:** high, medium, or low. High tasks are planned first.
3. **Due date and status:** only unfinished tasks that are due today (or overdue) are planned.
4. **Duration:** when two tasks have the same priority, the shorter one goes first so more tasks fit.
5. **Preferred time:** used to sort the plan in clock order and to warn about overlaps, but not to choose which tasks are planned.

I decided time and priority mattered most because those are the two things a busy owner can't ignore: there are only so many minutes, and things like medicine and feeding can't be skipped. Preferred times are softer, because the owner can usually move a walk, so I used them for warnings instead of hard rules.

**b. Tradeoffs**

My scheduler picks tasks by priority first and only checks times afterward to warn about overlaps. It does not move tasks to fix a conflict. For example, if Mochi's walk is 07:30–08:00 and Luna's medicine is at 07:45, both stay in the plan and the app shows a warning: "Morning walk (Mochi) at 07:30 overlaps Medication (Luna) at 07:45."

I think this is reasonable because the owner knows which task can move. Medicine might need to happen at an exact time, but a walk is usually flexible. If the app moved tasks on its own, it would have to guess, and it might push back something important without the owner noticing. A warning is simple, never crashes the program, and is easy to test. I did make the check look at the full duration of each task, not just exact time matches, because a 30-minute walk at 07:30 still blocks a task at 07:45 even though the start times are different.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code in VS Code for every phase: brainstorming the UML, turning it into class skeletons, writing the scheduling logic, writing tests, connecting the Streamlit UI, and writing documentation.

The most effective features were:
- **Design review:** I asked it to review my skeleton for missing relationships, and it found that tasks didn't know which pet they belonged to, which is why I added `pet_name`.
- **Plan-first editing:** I told it to always show me the exact code and ask before changing any file or running any command. That way I read every change before it happened.
- **Running checks for me:** it ran `pytest`, `main.py`, and a headless Streamlit test after each change, so I could see proof that the code worked instead of trusting it.
- **Explaining concepts:** for example, how a `lambda` key lets `sorted()` order `"HH:MM"` strings, and how `st.session_state` keeps my `Owner` object between reruns.

I worked in one main chat session, but I kept it organized by following the project phases one step at a time (UML → skeleton → logic → tests → UI → docs) and finishing each step before starting the next. Because the session remembered earlier decisions, like my rule to ask before changing files, I didn't have to repeat myself. The downside is that one long conversation gets crowded. Next time I'd start a new session for each phase, with a short summary of the design, so each one stays focused.

The most helpful prompts were specific ones like "review my skeleton for missing relationships or logic bottlenecks" and "suggest a lightweight conflict detection strategy that returns a warning instead of crashing."

**b. Judgment and verification**

When I added the first tests, the AI recommended adding a `conftest.py` file so plain `pytest` could find `pawpal_system.py`. I chose the other option instead: no extra file, and always run `python -m pytest`. It keeps the project simpler, and that's the command the assignment uses anyway. I also didn't let the AI change files on its own after the first step. I made it show me each change and wait for my approval.

To verify suggestions, I read the proposed code before saying yes, then checked the results: the tests (32 passing), the `main.py` output, and the headless app test. Checking the output paid off. When the demo output was pasted into the README, the task column was too narrow and "Flea medicine" ran into the pet name, so we widened the column and pasted the output again.

---

## 4. Testing and Verification

**a. What you tested**

I have 32 automated tests that cover:
- **Sorting:** tasks come back in clock order (even `"9:15"` vs `"12:00"`), untimed tasks go last, and priority ties go to the shorter task.
- **Recurrence:** completing a daily task creates a new one due tomorrow (weekly: +7 days), an overdue task's next copy isn't in the past, and one-time tasks don't repeat.
- **Conflicts:** same-time tasks (same pet or different pets) and partial overlaps are flagged, but back-to-back tasks, untimed tasks, and skipped tasks are not.
- **Planning:** the time limit is respected exactly, leftover time gets filled, a pet with no tasks gives an empty plan, and running the plan twice doesn't duplicate it.
- **Validation:** bad input raises a clear error, and a failed edit doesn't change the task.

These tests matter because the scheduler's job is to make decisions the owner trusts. If sorting, recurrence, or conflict checks were wrong, the plan could hide a missed medicine or a double-booked time, and the owner wouldn't know.

**b. Confidence**

I'm fairly confident, about 4 out of 5. All 32 tests pass, and I also checked the app by running `main.py` and a headless Streamlit test.

Next I would test:
- tasks that cross midnight (for example 23:30 for 60 minutes), which my conflict check doesn't handle
- a run that crosses midnight, by faking the date instead of using `date.today()`
- two tasks with the same title for the same pet
- automated tests for the Streamlit UI itself

---

## 5. Reflection

**a. What went well**

I'm most satisfied that the design stayed clean from start to finish. The four classes from my first UML are still the four classes in the final code, and each new feature fit into the class it belonged to: recurrence in `Pet` and `Task`, sorting, filtering, and conflicts in `Scheduler`. I'm also happy with the conflict warnings, because they catch real problems without crashing or taking control away from the owner.

**b. What you would improve**

- **Save data:** right now pets and tasks disappear when the browser page reloads. I'd save them to a JSON file.
- **Edit and remove in the app:** my classes have `edit_task`, `remove_task`, and `remove_pet`, but the UI doesn't use them yet.
- **Link tasks to pets better:** tasks point to their pet by name, so renaming a pet would break the link. I'd use an ID or a direct reference.
- **Smarter planning:** the greedy planner is easy to explain, but it doesn't always fit the most tasks. I could also suggest a free time slot when there's a conflict instead of only warning.

**c. Key takeaway**

Being the "lead architect" means the AI writes code fast, but I decide what the system should be. I set the design (four classes and their responsibilities), I set the rules (show me changes before making them), and I made the final calls, like choosing `python -m pytest` over an extra config file, and warnings instead of automatic rescheduling. The AI was most useful when I asked it specific questions and then checked its work with tests and real output. I learned that a clear design up front makes AI help much better, because every suggestion has to fit into a structure I already understand.
