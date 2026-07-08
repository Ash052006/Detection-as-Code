# Security Knowledge Base

Short explanations of dangerous commands and patterns: what they do, why they are dangerous, and what type of attack they represent.

---

## rm -rf /

**What it does:** Recursively deletes all files and directories starting from the root directory. The `-rf` flags mean no confirmation and force removal.

**Why it's dangerous:** This command can completely destroy the system and all data. It is irreversible.

**Attack type:** Destructive attack, sabotage. Attackers use it to wipe servers or cover tracks.

---

## IEX / Invoke-Expression

**What it does:** PowerShell cmdlet that executes a string as PowerShell code.

**Why it's dangerous:** Often used to download and run remote scripts from the internet. Attackers use it to execute malware or take control of the machine.

**Attack type:** Remote code execution (RCE), malware delivery.

---

## base64 -d

**What it does:** Decodes base64-encoded text. Often used in pipelines to decode a payload.

**Why it's dangerous:** Attackers encode malicious commands or payloads in base64 to hide them from simple log inspection or filters.

**Attack type:** Obfuscation, payload delivery.

---

## nc -e / netcat -e

**What it does:** Netcat with the `-e` option executes a program and pipes its input/output to the network connection.

**Why it's dangerous:** Used to create reverse shells: an attacker gets a remote command shell on the target machine.

**Attack type:** Reverse shell, remote access.

---

## bash -i

**What it does:** Starts an interactive bash shell.

**Why it's dangerous:** When combined with network redirection (e.g. to an attacker's machine), it is a common way to get a reverse shell for full control.

**Attack type:** Reverse shell.

---

## DownloadString / WebClient

**What it does:** In PowerShell, downloads the contents of a URL as a string. Often combined with Invoke-Expression to run the downloaded code.

**Why it's dangerous:** Attackers host malicious scripts and use this to pull and execute them on the victim machine without storing a file on disk.

**Attack type:** Living-off-the-land, malware download and execution.

---

## Invoke-Expression

**What it does:** Runs a PowerShell expression from a string. Same as IEX.

**Why it's dangerous:** Allows execution of arbitrary code. Often used with Get-Content or DownloadString to run scripts from files or the internet.

**Attack type:** Code execution, script-based attack.

---

## mimikatz / credential dumping

**What it does:** Tools or techniques that extract credentials (passwords, hashes) from memory or system files like SAM.

**Why it's dangerous:** Gives attackers reusable credentials to move laterally or escalate privileges.

**Attack type:** Credential theft, lateral movement.

---

## payload / meterpreter

**What it does:** Payloads are pieces of code that run after exploitation. Meterpreter is a Metasploit payload that provides an advanced shell and modules.

**Why it's dangerous:** Indicates active exploitation or post-exploitation tooling on the system.

**Attack type:** Exploitation, post-exploitation.

---

## xp_cmdshell / SQL injection

**What it does:** xp_cmdshell is a SQL Server feature that runs operating system commands. Often reached via SQL injection.

**Why it's dangerous:** Lets an attacker run arbitrary commands on the database server with the database service account's privileges.

**Attack type:** SQL injection, command execution.
