# Database Normalization: 1NF to BCNF

[← Tutorials](../README.md)

**Database normalization** is the process of organizing data to reduce
**redundancy** (the same fact stored many times) and improve **data
integrity** (the data stays accurate). We do this by splitting a large, messy
table into smaller, well-structured tables that can be joined back together.

This tutorial covers the four normal forms you need: **1NF, 2NF, 3NF and
BCNF**. Part A walks one example through all four. Part B is a practice
problem for you to solve, with a worked solution you can open when you're
done. Part C shows how to put the data back together with SQL, and Part D
shows how to draw the result as an ER diagram.

**Words you'll need:**

| Term | Meaning |
|---|---|
| **Primary key (PK)** | The column(s) that uniquely identify each row |
| **Composite key** | A primary key made of two or more columns |
| **Candidate key** | Any column set that *could* serve as the primary key |
| **Functional dependency** `A → B` | If you know `A`, you know `B` (e.g. `Student_ID → Name`) |
| **Determinant** | The left side of a dependency (`A` in `A → B`) |

---

## Part A — One example, four normal forms

### The starting point: an unnormalized table

A university tracks student enrollments in a single spreadsheet:

**Table: `University_Raw`**

| Student_ID | Name | Courses_Taken | Advisor | Advisor_Office |
|---|---|---|---|---|
| 101 | Alice | CS101, MATH200 | Dr. Smith | Room 404 |
| 102 | Bob | CS101 | Dr. Jones | Room 505 |
| 103 | Charlie | MATH200, PHYS101 | Dr. Smith | Room 404 |

### 1. First Normal Form (1NF)

**Requirements:**

1. **Atomic values:** every cell holds a single value — no lists or sets.
2. **Unique rows:** each row can be identified by a primary key.

**The problem:** `Courses_Taken` holds lists. You can't cleanly ask "who is
taking MATH200?" with a normal `WHERE` filter.

**The fix:** give every course its own row. The primary key becomes the
composite `(Student_ID, Course)`.

| Student_ID | Name | Course | Advisor | Advisor_Office |
|---|---|---|---|---|
| 101 | Alice | CS101 | Dr. Smith | Room 404 |
| 101 | Alice | MATH200 | Dr. Smith | Room 404 |
| 102 | Bob | CS101 | Dr. Jones | Room 505 |
| 103 | Charlie | MATH200 | Dr. Smith | Room 404 |
| 103 | Charlie | PHYS101 | Dr. Smith | Room 404 |

### 2. Second Normal Form (2NF)

**Requirements:**

1. The table is in 1NF.
2. **No partial dependencies:** every non-key column depends on the
   **whole** primary key, not just part of it.

**The problem:** the key is `(Student_ID, Course)`, but `Name`, `Advisor` and
`Advisor_Office` depend only on `Student_ID`. If Alice takes five courses,
her name and advisor are stored five times — and could be updated in four
places but forgotten in the fifth.

**The fix:** separate facts about the *student* from facts about the
*enrollment*.

**Table: `Students`** (PK: `Student_ID`)

| Student_ID | Name | Advisor | Advisor_Office |
|---|---|---|---|
| 101 | Alice | Dr. Smith | Room 404 |
| 102 | Bob | Dr. Jones | Room 505 |
| 103 | Charlie | Dr. Smith | Room 404 |

**Table: `Enrollments`** (PK: `Student_ID, Course`)

| Student_ID | Course |
|---|---|
| 101 | CS101 |
| 101 | MATH200 |
| 102 | CS101 |
| 103 | MATH200 |
| 103 | PHYS101 |

### 3. Third Normal Form (3NF)

**Requirements:**

1. The table is in 2NF.
2. **No transitive dependencies:** a non-key column must not depend on
   another non-key column.

**The problem:** in `Students`, `Advisor_Office` depends on `Advisor`, not on
`Student_ID`: `Student_ID → Advisor → Advisor_Office`. If Dr. Smith moves
offices, we must update every one of her students' rows.

**The fix:** move advisor details into their own table.

**Table: `Students`** (PK: `Student_ID`)

| Student_ID | Name | Advisor_ID |
|---|---|---|
| 101 | Alice | S01 |
| 102 | Bob | J01 |
| 103 | Charlie | S01 |

**Table: `Advisors`** (PK: `Advisor_ID`)

| Advisor_ID | Advisor_Name | Advisor_Office |
|---|---|---|
| S01 | Dr. Smith | Room 404 |
| J01 | Dr. Jones | Room 505 |

Now Dr. Smith's office is stored exactly once.

### 4. Boyce–Codd Normal Form (BCNF)

**Requirements:**

1. The table is in 3NF.
2. **Every determinant is a candidate key:** for every dependency `A → B`,
   `A` must uniquely identify the row.

BCNF is a stricter version of 3NF. Most 3NF tables are already in BCNF; the
difference shows up when a table has overlapping candidate keys. Here is a
new example.

**Business rules:** a student can have several advisors, one per subject.
Each advisor covers exactly one subject.

**Table: `Course_Assignments`** (PK: `Student_ID, Subject`)

| Student_ID | Subject | Advisor |
|---|---|---|
| 101 | Programming | Dr. White |
| 102 | Programming | Dr. White |
| 101 | Math | Dr. Green |

**The problem:** `Advisor → Subject` (Dr. White only does Programming), but
`Advisor` is not a candidate key of this table — Dr. White appears in two
rows. The table is in 3NF (`Subject` is part of a key, so the 3NF rule
doesn't catch it), but it is **not** in BCNF. The fact "Dr. White teaches
Programming" is stored once per student.

**The fix:** split the table so the determinant `Advisor` becomes a key.

**Table: `Student_Advisors`** (PK: `Student_ID, Advisor`)

| Student_ID | Advisor |
|---|---|
| 101 | Dr. White |
| 102 | Dr. White |
| 101 | Dr. Green |

**Table: `Advisor_Subjects`** (PK: `Advisor`)

| Advisor | Subject |
|---|---|
| Dr. White | Programming |
| Dr. Green | Math |

### How to remember it: the "oath"

> *"I swear that every column depends on the **key** (1NF), the **whole
> key** (2NF), and **nothing but the key** (3NF) — so help me **Codd**
> (BCNF)."*

---

## Part B — Practice problem: the medical clinic

A local health clinic tracks patient appointments in one spreadsheet. It
breaks every rule. Normalize it step by step, on paper or in a spreadsheet,
before opening each solution.

**Business rules:**

- Each patient has one phone number and one city.
- Each treatment code has one description; each doctor has one specialty.
- On a single visit a patient may receive several treatments, and **each
  treatment may be given by a different doctor**.

**Table: `Clinic_Raw`**

| Patient_ID | Name | Contact_Info | Appt_Date | Treatment_Code | Treatment_Desc | Doctor_ID | Doctor_Specialty |
|---|---|---|---|---|---|---|---|
| 1 | Alice | 555-0101, NYC | 2024-05-01 | T01, T02 | X-Ray, Blood Test | D101 | Radiology |
| 2 | Bob | 555-0202, LA | 2024-05-02 | T02 | Blood Test | D102 | General |
| 3 | Charlie | 555-0303, CHI | 2024-05-01 | T01, T03 | X-Ray, MRI | D101 | Radiology |

### Step 1 — Reach 1NF

- Which columns hold more than one value?
- How will you handle Alice receiving two treatments on one visit?
- What is the primary key afterwards?

<details>
<summary><b>Show the 1NF solution</b></summary>

`Contact_Info` holds two facts (phone and city), so it becomes two columns.
`Treatment_Code` and `Treatment_Desc` hold lists, so each treatment gets its
own row. The primary key is `(Patient_ID, Appt_Date, Treatment_Code)`.

| Patient_ID | Name | Phone | City | Appt_Date | Treatment_Code | Treatment_Desc | Doctor_ID | Doctor_Specialty |
|---|---|---|---|---|---|---|---|---|
| 1 | Alice | 555-0101 | NYC | 2024-05-01 | T01 | X-Ray | D101 | Radiology |
| 1 | Alice | 555-0101 | NYC | 2024-05-01 | T02 | Blood Test | D101 | Radiology |
| 2 | Bob | 555-0202 | LA | 2024-05-02 | T02 | Blood Test | D102 | General |
| 3 | Charlie | 555-0303 | CHI | 2024-05-01 | T01 | X-Ray | D101 | Radiology |
| 3 | Charlie | 555-0303 | CHI | 2024-05-01 | T03 | MRI | D101 | Radiology |

</details>

### Step 2 — Reach 2NF

- With the key `(Patient_ID, Appt_Date, Treatment_Code)`, which columns
  depend on only **part** of it?
- Does `Name` depend on `Treatment_Code`? Does `Treatment_Desc` depend on
  `Patient_ID`?

<details>
<summary><b>Show the 2NF solution</b></summary>

- `Name`, `Phone`, `City` depend only on `Patient_ID` → a `Patients` table.
- `Treatment_Desc` depends only on `Treatment_Code` → a `Treatments` table.
- `Doctor_ID` depends on the whole key (by the business rules, each treatment
  on each visit can have its own doctor), so it stays. `Doctor_Specialty`
  stays for now too — it doesn't depend on part of the key, it depends on
  `Doctor_ID`, which is a 3NF problem.

**Table: `Patients`** (PK: `Patient_ID`)

| Patient_ID | Name | Phone | City |
|---|---|---|---|
| 1 | Alice | 555-0101 | NYC |
| 2 | Bob | 555-0202 | LA |
| 3 | Charlie | 555-0303 | CHI |

**Table: `Treatments`** (PK: `Treatment_Code`)

| Treatment_Code | Treatment_Desc |
|---|---|
| T01 | X-Ray |
| T02 | Blood Test |
| T03 | MRI |

**Table: `Appointments`** (PK: `Patient_ID, Appt_Date, Treatment_Code`)

| Patient_ID | Appt_Date | Treatment_Code | Doctor_ID | Doctor_Specialty |
|---|---|---|---|---|
| 1 | 2024-05-01 | T01 | D101 | Radiology |
| 1 | 2024-05-01 | T02 | D101 | Radiology |
| 2 | 2024-05-02 | T02 | D102 | General |
| 3 | 2024-05-01 | T01 | D101 | Radiology |
| 3 | 2024-05-01 | T03 | D101 | Radiology |

</details>

### Step 3 — Reach 3NF

- In your tables, does any non-key column depend on another non-key column?

<details>
<summary><b>Show the 3NF solution</b></summary>

In `Appointments`, `Doctor_Specialty` depends on `Doctor_ID`, which is not
the key: `(Patient_ID, Appt_Date, Treatment_Code) → Doctor_ID →
Doctor_Specialty`. Move it to a `Doctors` table. `Patients` and `Treatments`
are unchanged.

**Table: `Doctors`** (PK: `Doctor_ID`)

| Doctor_ID | Specialty |
|---|---|
| D101 | Radiology |
| D102 | General |

**Table: `Appointments`** (PK: `Patient_ID, Appt_Date, Treatment_Code`)

| Patient_ID (FK) | Appt_Date | Treatment_Code (FK) | Doctor_ID (FK) |
|---|---|---|---|
| 1 | 2024-05-01 | T01 | D101 |
| 1 | 2024-05-01 | T02 | D101 |
| 2 | 2024-05-02 | T02 | D102 |
| 3 | 2024-05-01 | T01 | D101 |
| 3 | 2024-05-01 | T03 | D101 |

If we need a specialty, we `JOIN` to `Doctors`. If Dr. D101 changes
specialty, we update one row.

</details>

### Step 4 — Check BCNF

For each of your four tables, list its functional dependencies. Is every
determinant a candidate key?

<details>
<summary><b>Show the BCNF check</b></summary>

| Table | Dependencies | Determinant is a key? |
|---|---|---|
| `Patients` | `Patient_ID → Name, Phone, City` | ✅ `Patient_ID` is the PK |
| `Treatments` | `Treatment_Code → Treatment_Desc` | ✅ PK |
| `Doctors` | `Doctor_ID → Specialty` | ✅ PK |
| `Appointments` | `(Patient_ID, Appt_Date, Treatment_Code) → Doctor_ID` | ✅ PK |

Every determinant is a key, so all four tables are in **BCNF** — the 3NF
design already satisfies it.

**What would break BCNF?** Keeping `Specialty` in `Appointments` next to
`Doctor_ID`. Then `Doctor_ID → Specialty` would hold inside `Appointments`,
but `Doctor_ID` is not a key there (D101 appears in four rows), so the
"D101 is a radiologist" fact would be repeated on every appointment. That is
exactly the redundancy the `Doctors` table removes.

</details>

---

## Part C — Putting the data back together with SQL

Normalization doesn't lose information: joins rebuild the original view
whenever we need it. We **store** data normalized and **present** it however
the user wants.

The four tables in DuckDB:

```sql
CREATE TABLE Patients (
    Patient_ID INTEGER PRIMARY KEY,
    Name       VARCHAR,
    Phone      VARCHAR,
    City       VARCHAR
);
INSERT INTO Patients VALUES
    (1, 'Alice', '555-0101', 'NYC'),
    (2, 'Bob', '555-0202', 'LA'),
    (3, 'Charlie', '555-0303', 'CHI');

CREATE TABLE Doctors (
    Doctor_ID VARCHAR PRIMARY KEY,
    Specialty VARCHAR
);
INSERT INTO Doctors VALUES ('D101', 'Radiology'), ('D102', 'General');

CREATE TABLE Treatments (
    Treatment_Code VARCHAR PRIMARY KEY,
    Treatment_Desc VARCHAR
);
INSERT INTO Treatments VALUES ('T01', 'X-Ray'), ('T02', 'Blood Test'), ('T03', 'MRI');

CREATE TABLE Appointments (
    Patient_ID     INTEGER REFERENCES Patients,
    Appt_Date      DATE,
    Treatment_Code VARCHAR REFERENCES Treatments,
    Doctor_ID      VARCHAR REFERENCES Doctors,
    PRIMARY KEY (Patient_ID, Appt_Date, Treatment_Code)
);
INSERT INTO Appointments VALUES
    (1, '2024-05-01', 'T01', 'D101'),
    (1, '2024-05-01', 'T02', 'D101'),
    (2, '2024-05-02', 'T02', 'D102'),
    (3, '2024-05-01', 'T01', 'D101'),
    (3, '2024-05-01', 'T03', 'D101');
```

### Rebuild one row per treatment

`Appointments` holds the IDs; the three lookup tables supply the names.

```sql
SELECT
    p.Patient_ID,
    p.Name,
    p.Phone || ', ' || p.City AS Contact,
    a.Appt_Date,
    a.Treatment_Code,
    t.Treatment_Desc,
    a.Doctor_ID,
    d.Specialty
FROM Appointments AS a
JOIN Patients   AS p ON a.Patient_ID     = p.Patient_ID
JOIN Doctors    AS d ON a.Doctor_ID      = d.Doctor_ID
JOIN Treatments AS t ON a.Treatment_Code = t.Treatment_Code
ORDER BY a.Appt_Date, p.Name, a.Treatment_Code;
```

```
┌────────────┬─────────┬───────────────┬────────────┬────────────────┬────────────────┬───────────┬───────────┐
│ Patient_ID │  Name   │    Contact    │ Appt_Date  │ Treatment_Code │ Treatment_Desc │ Doctor_ID │ Specialty │
├────────────┼─────────┼───────────────┼────────────┼────────────────┼────────────────┼───────────┼───────────┤
│          1 │ Alice   │ 555-0101, NYC │ 2024-05-01 │ T01            │ X-Ray          │ D101      │ Radiology │
│          1 │ Alice   │ 555-0101, NYC │ 2024-05-01 │ T02            │ Blood Test     │ D101      │ Radiology │
│          3 │ Charlie │ 555-0303, CHI │ 2024-05-01 │ T01            │ X-Ray          │ D101      │ Radiology │
│          3 │ Charlie │ 555-0303, CHI │ 2024-05-01 │ T03            │ MRI            │ D101      │ Radiology │
│          2 │ Bob     │ 555-0202, LA  │ 2024-05-02 │ T02            │ Blood Test     │ D102      │ General   │
└────────────┴─────────┴───────────────┴────────────┴────────────────┴────────────────┴───────────┴───────────┘
```

### Rebuild the original "messy" format

To get back the very first layout — Alice's treatments as `T01, T02` in one
cell — group by visit and glue the values together with `STRING_AGG`
(DuckDB also accepts the name `LISTAGG`):

```sql
SELECT
    p.Name,
    a.Appt_Date,
    STRING_AGG(a.Treatment_Code, ', ' ORDER BY a.Treatment_Code) AS Treatment_Codes,
    STRING_AGG(t.Treatment_Desc, ', ' ORDER BY a.Treatment_Code) AS Treatment_Descs,
    d.Specialty
FROM Appointments AS a
JOIN Patients   AS p ON a.Patient_ID     = p.Patient_ID
JOIN Doctors    AS d ON a.Doctor_ID      = d.Doctor_ID
JOIN Treatments AS t ON a.Treatment_Code = t.Treatment_Code
GROUP BY p.Name, a.Appt_Date, d.Specialty
ORDER BY a.Appt_Date, p.Name;
```

```
┌─────────┬────────────┬─────────────────┬───────────────────┬───────────┐
│  Name   │ Appt_Date  │ Treatment_Codes │  Treatment_Descs  │ Specialty │
├─────────┼────────────┼─────────────────┼───────────────────┼───────────┤
│ Alice   │ 2024-05-01 │ T01, T02        │ X-Ray, Blood Test │ Radiology │
│ Charlie │ 2024-05-01 │ T01, T03        │ X-Ray, MRI        │ Radiology │
│ Bob     │ 2024-05-02 │ T02             │ Blood Test        │ General   │
└─────────┴────────────┴─────────────────┴───────────────────┴───────────┘
```

**The full circle:**

1. **Storage (BCNF):** four tables, each fact stored once.
2. **Logic (SQL):** joins connect the related IDs.
3. **Presentation:** aggregate and format the output however the reader
   needs — without breaking the rules underneath.

---

## Part D — Drawing it: Entity–Relationship Diagrams

An **Entity–Relationship Diagram (ERD)** is a visual blueprint of a database:
the *things* you track (entities) and how they connect (relationships).
Normalization is the mathematical way to split tables; an ERD is the visual
way to check that the structure makes sense to a human.

Further reading: [What is an Entity Relationship Diagram?](https://www.visual-paradigm.com/guide/data-modeling/what-is-entity-relationship-diagram/)
(Visual Paradigm) · [ERDs in draw.io](https://drawio-app.com/erd/)

### The building blocks

- **Entities** (rectangles): the main "nouns" — tables such as `Patient`, `Doctor`.
- **Attributes** (ovals, or listed inside the rectangle): the columns. The
  primary key is usually underlined.
- **Relationships** (lines, sometimes diamonds): the "verbs" connecting them
  — a patient *has* appointments.

### Cardinality and crow's feet

| Type | Meaning | Example |
|---|---|---|
| **1:1** | One row matches exactly one other | A person and their passport |
| **1:N** | One row matches many | One doctor has many appointments |
| **M:N** | Many match many | Students and courses |

In crow's-foot notation, the "many" end of a line ends in a three-pronged
fork. A relational database can't store M:N directly: it is broken into two
1:N relationships with a **junction table** in the middle — like
`Enrollments` between students and courses in Part A.

### The clinic database as an ERD

```
 PATIENTS 1 ────< APPOINTMENTS >──── 1 DOCTORS
                       V
                       │
                       1
                  TREATMENTS
```

Each `>` / `<` / `V` marks the "many" end: one patient has many
appointments, one doctor handles many appointment rows, and one treatment
appears in many appointment rows. `Appointments` is the junction table
connecting the other three.

**Try it:** draw this diagram yourself in draw.io with crow's-foot notation,
listing each table's columns and marking the primary and foreign keys.

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
