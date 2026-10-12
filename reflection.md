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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

My scheduler picks tasks by priority first and only checks times afterward to warn about overlaps. It does not move tasks to fix a conflict. For example, if Mochi's walk is 07:30–08:00 and Luna's medicine is at 07:45, both stay in the plan and the app shows a warning: "Morning walk (Mochi) at 07:30 overlaps Medication (Luna) at 07:45."

I think this is reasonable because the owner knows which task can move. Medicine might need to happen at an exact time, but a walk is usually flexible. If the app moved tasks on its own, it would have to guess, and it might push back something important without the owner noticing. A warning is simple, never crashes the program, and is easy to test. I did make the check look at the full duration of each task, not just exact time matches, because a 30-minute walk at 07:30 still blocks a task at 07:45 even though the start times are different.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
