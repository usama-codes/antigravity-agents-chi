# User Story Template

Use this template for every user story. Do not omit any section. If a section is not applicable, write "N/A" with a brief justification.

---

### US-{epic_abbrev}-{number}: {Concise, Action-Oriented Title}

**Priority**: {P0 | P1 | P2 | P3}
**Category**: {CORE | SUPPORTING | ENHANCEMENT}

**As a** {specific user persona — e.g., "authenticated free-tier user", NOT just "user"}
**I want to** {specific action the user takes — e.g., "edit my display name and avatar on the profile screen"}
**So that** {concrete user benefit — e.g., "other users can recognize me in conversations"}

---

#### Acceptance Criteria

> Every criterion must be **binary** (pass/fail), **specific** (exact values/states), and **testable** (a QA engineer can write an automated test from it).

##### Happy Path
- [ ] **AC-{story_number}.1**: Given {precise precondition with specific state}, when {exact user action}, then {exact observable result with specific values/states}
- [ ] **AC-{story_number}.2**: ...

##### Validation
- [ ] **AC-{story_number}.V1**: Given {input field context}, when the user enters {specific invalid input — e.g., "a display name shorter than 2 characters"}, then {exact error behavior — e.g., "a red error label reading 'Display name must be 2-50 characters' appears below the field and the Save button remains disabled"}
- [ ] **AC-{story_number}.V2**: ...

##### Error Handling
- [ ] **AC-{story_number}.E1**: Given the user has submitted valid data, when the API returns a {specific error — e.g., "HTTP 500 Internal Server Error"}, then {exact error UX — e.g., "a SnackBar with the message 'Something went wrong. Please try again.' appears for 4 seconds and the form remains editable with the user's data preserved"}
- [ ] **AC-{story_number}.E2**: Given the device has no network connectivity, when the user attempts to {action}, then {exact offline behavior}

##### Loading States
- [ ] **AC-{story_number}.L1**: Given the user has triggered {action}, when the API request is in flight, then {exact loading UX — e.g., "the Save button shows a 24x24 CircularProgressIndicator replacing the button text, and all form fields become disabled"}

##### Empty States
- [ ] **AC-{story_number}.EM1**: Given {condition for empty state — e.g., "the user has never set a display name"}, when {trigger — e.g., "the profile screen loads"}, then {exact empty state UX — e.g., "the display name field shows placeholder text 'Enter your display name' in grey italic"}

##### Edge Cases
- [ ] **AC-{story_number}.EC1**: Given {edge condition — e.g., "the user double-taps the Save button rapidly"}, when {specific timing/interaction}, then {expected behavior — e.g., "only one API request is sent and subsequent taps are ignored until the first request completes"}
- [ ] **AC-{story_number}.EC2**: ...

##### Accessibility (where applicable)
- [ ] **AC-{story_number}.A1**: Given a screen reader is active, when the user navigates to {element}, then {exact semantic label — e.g., "the avatar image announces 'Profile photo. Double tap to change.'"}

---

#### UI Components Needed

| Component | Type | Screen(s) Used On | Notes |
|---|---|---|---|
| {ComponentName} | {Screen / Widget / Dialog / BottomSheet / Overlay} | {list of screens} | {brief notes on props, states, or behavior} |
| ... | ... | ... | ... |

---

#### Technical Notes

##### Data Models
- {Model name}: {brief description of fields and relationships}

##### API Endpoints
- `{METHOD} {/path}` — {purpose} — Request: `{brief shape}` — Response: `{brief shape}`

##### State Management
- {What state is managed, where, and key transitions}

##### Dependencies
- **Depends on**: {list of other US-IDs or external prerequisites}
- **Blocks**: {list of other US-IDs that depend on this story}

##### Packages
- `{package_name}` — {purpose}

---

#### Complexity: {S | M | L}

**Justification**: {1-2 sentences explaining the sizing — e.g., "M because it involves one new screen with a form, one API call, and local validation logic, but no complex state management or custom widgets."}

> ⚠️ If complexity is **XL**, this story MUST be broken down into smaller stories. XL stories are not permitted in the final requirements document.
