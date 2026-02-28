---
description: "Interact with the Hevy workout platform API via curl/bash. Covers auth setup, workouts, exercises, routines, and pagination."
---

# Hevy API — Skill Reference

Interact with the [Hevy](https://hevy.com) workout platform via curl/bash.
Requires a **Hevy PRO** subscription.

**Base URL:** `https://api.hevyapp.com`

---

## First-time Setup (agent checklist)

**Run this check first. If the variable is missing, follow the setup steps below before proceeding.**

```sh
# macOS/Linux
echo "${HEVY_API_KEY:?HEVY_API_KEY is not set — follow the setup steps in this skill}"

# Windows (PowerShell)
if (-not $env:HEVY_API_KEY) { throw "HEVY_API_KEY is not set — follow the setup steps in this skill" }
```

### Step 1 — Get your API key

1. Open the Hevy app on your phone
2. Go to **Profile → Settings → API**
3. Copy your API key (requires Hevy PRO)

### Step 2 — Store the key (pick your platform)

---

#### macOS — Keychain (recommended: set and forget)

Store once:
```sh
security add-generic-password -a "$USER" -s HEVY_API_KEY -w "your_api_key_here"
```

Load automatically on every shell session — add to `~/.zshrc`:
```sh
export HEVY_API_KEY=$(security find-generic-password -a "$USER" -s HEVY_API_KEY -w 2>/dev/null)
```

Then reload:
```sh
source ~/.zshrc
```

To update the key later:
```sh
security delete-generic-password -a "$USER" -s HEVY_API_KEY
security add-generic-password -a "$USER" -s HEVY_API_KEY -w "new_api_key_here"
```

---

#### macOS/Linux — direnv (alternative: project-scoped)

Install:
```sh
brew install direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc && source ~/.zshrc
```

Create `.envrc` in the project root:
```sh
echo 'export HEVY_API_KEY=your_api_key_here' > .envrc
direnv allow .
```

Add `.envrc` to `.gitignore`:
```sh
echo '.envrc' >> .gitignore
```

Key loads automatically when you `cd` into the project directory.

---

#### Windows — User Environment Variable (recommended: set and forget)

In PowerShell (run once, persists permanently):
```powershell
[System.Environment]::SetEnvironmentVariable("HEVY_API_KEY", "your_api_key_here", "User")
```

Restart your terminal. Verify:
```powershell
$env:HEVY_API_KEY
```

To update later, run the same command with the new key.

> **More secure alternative (Windows Credential Manager):**
> ```powershell
> # Store
> Install-Module Microsoft.PowerShell.SecretManagement, Microsoft.PowerShell.SecretStore -Scope CurrentUser
> Register-SecretVault -Name LocalStore -ModuleType Microsoft.PowerShell.SecretStore
> Set-Secret -Vault LocalStore -Name HEVY_API_KEY -Secret "your_api_key_here"
>
> # Add to PowerShell profile (~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1)
> $env:HEVY_API_KEY = Get-Secret -Vault LocalStore -Name HEVY_API_KEY -AsPlainText
> ```

---

### Step 3 — Verify

```sh
# macOS/Linux
curl -s -H "api-key: $HEVY_API_KEY" https://api.hevyapp.com/v1/workouts?pageSize=1 | jq .

# Windows (PowerShell)
curl -s -H "api-key: $env:HEVY_API_KEY" https://api.hevyapp.com/v1/workouts?pageSize=1 | ConvertFrom-Json
```

A valid response returns a `workouts` array. A 401 means the key is wrong or missing.

---

## Workouts

```sh
# List workouts (paginated)
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/workouts?page=1&pageSize=10"

# Get a single workout
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/workouts/{workoutId}"

# Get total workout count
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/workouts/count"

# Create a workout
curl -s -X POST \
  -H "api-key: $HEVY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "workout": {
      "title": "Morning Push",
      "start_time": "2026-02-28T07:00:00Z",
      "end_time": "2026-02-28T08:00:00Z",
      "exercises": [
        {
          "exercise_template_id": "TEMPLATE_ID",
          "sets": [
            { "type": "normal", "weight_kg": 80, "reps": 8 }
          ]
        }
      ]
    }
  }' \
  "https://api.hevyapp.com/v1/workouts"

# Update a workout
curl -s -X PUT \
  -H "api-key: $HEVY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "workout": { "title": "Updated Title" } }' \
  "https://api.hevyapp.com/v1/workouts/{workoutId}"
```

---

## Exercise Templates

```sh
# List exercise templates (paginated)
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/exercise_templates?page=1&pageSize=20"

# Get a single exercise template
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/exercise_templates/{exerciseTemplateId}"
```

---

## Exercise History

```sh
# Get history for an exercise (all time)
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/exercise_history/{exerciseTemplateId}"

# With date filters (ISO 8601)
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/exercise_history/{exerciseTemplateId}?start_date=2026-01-01&end_date=2026-02-28"
```

---

## Routines

```sh
# List routines
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/routines?page=1&pageSize=10"

# Get a single routine
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/routines/{routineId}"

# Create a routine
curl -s -X POST \
  -H "api-key: $HEVY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "routine": {
      "title": "Push Day",
      "folder_id": null,
      "exercises": [
        {
          "exercise_template_id": "TEMPLATE_ID",
          "sets": [
            { "type": "normal", "weight_kg": 0, "reps": 10 }
          ]
        }
      ]
    }
  }' \
  "https://api.hevyapp.com/v1/routines"
```

---

## Routine Folders

```sh
# List folders
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/routine_folders"

# Create a folder
curl -s -X POST \
  -H "api-key: $HEVY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "routine_folder": { "title": "Strength" } }' \
  "https://api.hevyapp.com/v1/routine_folders"
```

---

## Common Patterns

**Parse JSON with jq:**
```sh
# Get titles of last 5 workouts
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/workouts?page=1&pageSize=5" \
  | jq '.workouts[].title'

# Find exercise template ID by name
curl -s -H "api-key: $HEVY_API_KEY" \
  "https://api.hevyapp.com/v1/exercise_templates?page=1&pageSize=100" \
  | jq '.exercise_templates[] | select(.title | test("bench press"; "i")) | {id, title}'
```

**Pagination loop:**
```sh
page=1
while true; do
  result=$(curl -s -H "api-key: $HEVY_API_KEY" \
    "https://api.hevyapp.com/v1/workouts?page=$page&pageSize=10")
  count=$(echo "$result" | jq '.workouts | length')
  echo "$result" | jq '.workouts[].title'
  [ "$count" -lt 10 ] && break
  ((page++))
done
```

---

## Reference

- Full docs: https://api.hevyapp.com/docs/
- `pageSize` max: 10 (workouts/routines), larger values allowed for exercise templates
- HTTP 401 → key missing or invalid
- HTTP 403 → Hevy PRO required
