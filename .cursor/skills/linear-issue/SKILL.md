---
name: linear-issue
description: Manages Linear via MCP. Use for creating issues, listing/updating issues, managing projects, teams, milestones, initiatives, cycles, labels, comments, attachments, and status updates. For issue creation, follow templates in references/.
---

# Linear Management (MCP)

Use the **Linear MCP** for all Linear operations. **Keep issues scannable—no one reads walls of text.**

## Principles

- **Use MCP.** All Linear actions go through `call_mcp_tool`—never guess or simulate.
- **Clear and concise.** Form sentences that are easy to scan—no fluff, no loss of detail.
- **Complete the form.** For issue creation, strive to include all details in every section of the template.
- **No metadata in content.** Status, priority, assignee, labels, etc. go into Linear issue fields; do not add a Metadata section in the issue body.
- **Ask before writing.** Clarify assignee, priority, and any ambiguity—don't guess.
- **Link, don't duplicate.** Reference docs, Figma, or tickets instead of pasting content.

## MCP Tools (by action)

| Action             | Tools                                                                          |
| ------------------ | ------------------------------------------------------------------------------ |
| **Issues**         | `create_issue`, `update_issue`, `get_issue`, `list_issues`                     |
| **Projects**       | `create_project`, `update_project`, `get_project`, `list_projects`             |
| **Teams**          | `get_team`, `list_teams`                                                       |
| **Milestones**     | `create_milestone`, `update_milestone`, `get_milestone`, `list_milestones`     |
| **Initiatives**    | `create_initiative`, `update_initiative`, `get_initiative`, `list_initiatives` |
| **Cycles**         | `list_cycles`                                                                  |
| **Labels**         | `list_issue_labels`, `create_issue_label`, `list_project_labels`               |
| **Statuses**       | `list_issue_statuses`, `get_issue_status`                                      |
| **Comments**       | `create_comment`, `list_comments`                                              |
| **Attachments**    | `create_attachment`, `get_attachment`, `delete_attachment`                     |
| **Documents**      | `create_document`, `update_document`, `get_document`, `list_documents`         |
| **Users**          | `get_user`, `list_users`                                                       |
| **Status updates** | `get_status_updates`, `save_status_update`, `delete_status_update`             |

**Always check the tool schema** before calling.

## Title Rules

- **Max ~60 characters.** Titles should fit on one line in a sidebar.
- **Imperative verb, no filler.** Start with an action word: Add, Fix, Update, Remove, Refactor, Support, Move, etc.
- **No "via", "using", "in order to" chains.** Trim prepositional clauses — one clear idea per title.
- **No "and".** If a title needs "and", split it into two issues.
- **Examples:**
  - ✅ `Set membership role at invite creation`
  - ✅ `Add E2E test infrastructure`
  - ❌ `Set org role in membership metadata at invite creation, not via webhook` (too long)
  - ❌ `Refactor the auth service to support new JWT claims and update ABAC` (compound)

## Issue Creation Workflow

When **creating** an issue:

1. **Clarify** (ask if not provided): assignee, priority, any missing context.
2. **Pick template** from intent:
   - Bug → [references/bug_template.md](references/bug_template.md)
   - General → [references/general_issue_template.md](references/general_issue_template.md)
   - Backend → [references/backend_template.md](references/backend_template.md)
   - Frontend → [references/frontend_template.md](references/frontend_template.md)
3. **Fill the form.** Complete every section (except Metadata—that goes to issue fields). Write clearly and concisely.
4. **Labels** from [references/available_labels.md](references/available_labels.md)—only what fits. Pass labels, assignee, priority, etc. as MCP parameters, not in the body.
5. **Call Linear MCP:** Use the relevant MCP tool to create the issue.

## Other Actions

- **List/search:** Use `list_issues`, `list_projects`, etc. with filters (`query`, `team`, `state`, etc.).
- **Update:** Use `update_issue`, `update_project`, etc. with the target ID and changed fields.
- **Get details:** Use `get_issue`, `get_project`, etc. when you need full data for an ID.

## Output

Return the result from the MCP call (e.g., issue URL, list of items, updated object).
