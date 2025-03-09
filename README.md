# GarbageScripts

While not actually garbage, this is just going to be a random collection of scripts that do things that I need. I make these all the time and it'd be nice to have them somewhere in particular.

## Overview

GarbageScripts is a growing repository of various Python scripts for everyday tasks. This is not a tightly organized project; rather, it's a personal collection where I store utilities and scripts that I find useful. New scripts will be added gradually as needs arise.

## Repository Structure

```
GarbageScripts/
├── cmd/              # Contains cross-platform command wrappers (Bash, Windows CMD, PowerShell)
│   └── README.md     # Detailed installation and usage instructions for the command wrappers
├── python/           # Contains the core Python scripts
│   ├── compare_directories.py
│   └── rename_uuid.py
└── README.md         # This top-level README
```

## Current Scripts

- **compare_directories.py**  
  A utility that compares the contents of two directories and reports any differences. It’s handy for verifying synchronization or identifying discrepancies between directory structures.

- **rename_uuid.py**  
  A tool designed to rename files using UUIDs to ensure uniqueness. This script could help manage files with duplicate names or organize files where unique identifiers are needed. It's mostly used for helping to generate unique hierarchies to test other tools with.

*For detailed installation and usage instructions, please refer to the [README.md in the `cmd` directory](cmd/README.md).*

## Contributing

This repository is primarily a personal collection of useful scripts, so contributions aren’t actively managed. However, if you find something useful or have suggestions, feel free to fork and modify the repository for your own use.

## Future Plans

I plan to continue adding more scripts as I develop new utilities or discover interesting tasks that can be automated. Stay tuned for updates!
