# Getting the Course Files with Git

**Optional.** Downloading the ZIP (see `software_installation/`, Step 0) is all
you need for this course. Use Git only if you already know it or want to learn
it — the payoff is that **one command picks up each week's new material**
instead of downloading a new ZIP.

---

## 1. Check that Git is installed

Open a terminal (macOS: **Terminal**; Windows: **Command Prompt** or
**PowerShell**) and run:

```
git --version
```

If you see a version number, skip to Step 2. Otherwise:

- **macOS:** run `xcode-select --install` and accept the prompt (this installs
  Apple's command-line tools, which include Git).
- **Windows:** download and run the installer from <https://git-scm.com/download/win>,
  accepting the defaults, then open a **new** terminal window.

## 2. Clone the course repository (once)

Go to the folder where you keep your course work, then clone:

```
cd Documents
git clone https://github.com/mahmoudparsian/MSIS-2402.git
cd MSIS-2402
```

You now have a folder called **`MSIS-2402`** — the same contents as the ZIP,
plus Git's history. (The ZIP version of the folder is called `MSIS-2402-main`;
the files inside are identical.)

## 3. Get each week's new material

From inside the `MSIS-2402` folder:

```
git pull
```

That's it — new and updated files appear in place.

## 4. Keep your own work separate (so `git pull` never fails)

`git pull` refuses to run if you have **edited** a file that the course has also
updated, because it won't overwrite your work. Avoid that entirely by **never
editing the course files in place**:

- Make your own folder **outside** `MSIS-2402` (for example
  `Documents/MSIS-2402-my-work`).
- **Copy** a lab or notebook there before you start working on it.

## 5. If `git pull` complains anyway

If you did edit a course file and `git pull` stops with a message like
*"Your local changes to the following files would be overwritten"*:

1. **Save a copy of your work first** — copy any file you changed to your own
   work folder (Step 4).
2. Throw away your edits to the course files and pull again:

   ```
   git restore .
   git pull
   ```

`git restore .` discards **all** changes you made to files Git is tracking in
this folder — that's why step 1 matters. Files you *added* yourself are not
touched.

If things get truly tangled, delete the `MSIS-2402` folder (after copying out
anything of yours) and clone again — it takes a minute and always works.

## 6. What you don't need

You don't need a GitHub account, and you will **not** push anything back —
the course repository is read-only for students. Submit your labs on Camino
([how](../../course_information/ASSIGNMENTS_and_GRADING.md#3-how-to-submit-a-lab)), not through Git.
