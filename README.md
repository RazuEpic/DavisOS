# DavisOS
Tribute to Terry
(My 3rd attempt at trying to make this repository)

## Features

### 🔹 File Management
- `make file <name>` → Create a new file
- `view file <name>` → View a file’s contents
- `open file <name>` → Open and edit a file
- `delete file <name>` → Delete a file
- `rename file <old> <new>` → Rename a file
- `copy file <name> <path>` → Copy file to another directory
- `move file <name> <path>` → Move file to another directory

### 🔹 Directory Management
- `make dir <name>` → Create a new directory
- `delete dir <name>` → Delete a directory
- `goto <path>` → Change working directory
- `list` → List files and directories
- `here` → Show current working directory
- `move dir <src> <dest>` → Move a directory

### 🔹 System & Environment
- `setext <.ext>` → Change the default file extension
- `osinfo` → Display system information

### 🔹 Job Control
- `run <command>` → Run external system commands
- `jobs` → List running jobs
- `kill <job_id>` → Kill a job by ID

### 🔹 Utilities
- `calc` → Calculator (interactive or one-liner math)
- `echo <text>` → Print text back to the terminal
- `sleep <seconds>` → Pause execution
- `history` → Show command history
- `!!` → Repeat the last command

### 🔹 Therapist (Mini Program)
- `call therapist` → Launch the built-in AI-like therapist
  - Asks personal, reflective questions
  - Responds empathetically to positive/negative answers
  - Type `:wq` to exit the session

---

## 🔹 Aliases
To make commands feel more natural:
- `g` → `goto`
- `l` → `list`

---

## 🔹 Example Session

```bash
user:~ >> make dir projects
Created directory as projects

user:~ >> goto projects
Moved to /home/user/projects

user:~/projects >> make file notes
Created file notes.txt

user:~/projects >> call therapist
Therapist: Hello. I’m here to listen. Type ':wq' to exit at any time.
Therapist: How are you feeling today?
