# Command Wrappers Directory

This directory contains wrapper scripts for calling Python scripts located in the sibling `python` directory from the command line. The wrappers are provided in three formats to support cross-platform usage:

- **Bash wrappers**: For macOS, Linux, and other Unix-like systems.
- **Windows CMD wrappers**: For the classic Windows command prompt.
- **Windows PowerShell wrappers**: For modern Windows PowerShell environments.

Each wrapper is designed to automatically locate the corresponding Python script relative to the `cmd` directory and forward all command-line arguments.

---

## How It Works

The wrappers determine their own directory and then construct a path to the Python script in the `python` directory (assumed to be at the same level as the `cmd` directory). For example, if your repository structure is:

```
your_repo/
├── cmd/
│   ├── compare_directories      (bash wrapper)
│   ├── compare_directories.cmd  (Windows CMD wrapper)
│   ├── compare_directories.ps1  (Windows PowerShell wrapper)
│   ├── rename_uuid              (bash wrapper)
│   ├── rename_uuid.cmd          (Windows CMD wrapper)
│   └── rename_uuid.ps1          (Windows PowerShell wrapper)
└── python/
    ├── compare_directories.py
    └── rename_uuid.py
```

then each wrapper script in `cmd` will call the corresponding Python script from the `python` directory, passing along any command-line arguments.

---

## Adding the `cmd` Directory to Your PATH

For convenient access to these wrappers from any location in your terminal, add the `cmd` directory to your system's PATH. Follow the instructions for your operating system below.

### macOS

1. **Open Terminal.**
2. **Determine your shell configuration file:**
   - For Bash: Edit `~/.bash_profile` or `~/.bashrc`
   - For Zsh (default in recent macOS versions): Edit `~/.zshrc`
3. **Add the following line** (replace `/path/to/your_repo/cmd` with the actual path):

   ```bash
   export PATH="/path/to/your_repo/cmd:$PATH"
   ```

4. **Save the file and refresh your shell configuration** by running:

   ```bash
   source ~/.bash_profile   # for Bash
   source ~/.zshrc          # for Zsh
   ```

### Linux

1. **Open your terminal.**
2. **Edit your shell configuration file:**
   - For Bash: Edit `~/.bashrc` (or `~/.bash_profile` on some distributions)
   - For Zsh: Edit `~/.zshrc`
3. **Add the following line** to the file (replace `/path/to/your_repo/cmd` with the actual path):

   ```bash
   export PATH="/path/to/your_repo/cmd:$PATH"
   ```

4. **Save the file and reload the configuration** by executing:

   ```bash
   source ~/.bashrc   # for Bash
   source ~/.zshrc    # for Zsh
   ```

### Windows

#### Using System Properties

1. **Open the Start Menu** and search for "Environment Variables."
2. **Click on "Edit the system environment variables."**
3. In the **System Properties** window, click on the **"Environment Variables…"** button.
4. Under **User variables** or **System variables**, select the **"Path"** variable and click **"Edit."**
5. Click **"New"** and add the full path to your `cmd` directory (for example, `C:\path\to\your_repo\cmd`).
6. Click **OK** to close all dialog boxes and apply the changes.

#### Using Command Prompt

Alternatively, you can add the path temporarily by opening a Command Prompt and typing:

```batch
set PATH=C:\path\to\your_repo\cmd;%PATH%
```

To permanently set it for your user account, run:

```batch
setx PATH "C:\path\to\your_repo\cmd;%PATH%"
```

#### Using PowerShell

In PowerShell, you can temporarily add the directory by running:

```powershell
$env:PATH = "C:\path\to\your_repo\cmd;" + $env:PATH
```

For a permanent change, update the Environment Variables via System Properties as described above.

---

## Usage

Once the `cmd` directory is added to your PATH, you can simply type the name of the wrapper script (without the extension on Unix-like systems) in your terminal or command prompt to run the corresponding Python script. For example:

- **macOS/Linux:**

  ```bash
  compare_directories [arguments...]
  ```

- **Windows CMD:**

  ```batch
  compare_directories [arguments...]
  ```

- **Windows PowerShell:**

  ```powershell
  .\compare_directories.ps1 [arguments...]
  ```

Each call will automatically forward any provided arguments to the corresponding Python script in the `python` directory.

---

By following these instructions, you can seamlessly integrate your command wrappers into your system environment and invoke your Python scripts from anywhere on your system.
