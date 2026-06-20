# CareRoute AI — Frontend

Plain HTML/CSS/vanilla JS. No build step — just open `index.html` in a browser,
or open the folder in VS Code with the "Live Server" extension for auto-reload.

## Pages

| File | Screen |
|---|---|
| `index.html` | Landing page |
| `signup-user.html` | Patient registration |
| `signup-doctor.html` | Doctor registration (with degree upload) |
| `login.html` | Shared login (toggle Patient / Doctor) |
| `upload.html` | Upload Your Medical Document |
| `processing.html` | Analyzing / Processing screen |
| `dashboard.html` | Results Dashboard (Patient View) |
| `history.html` | Document history |
| `my-questions.html` | Patient's question tracker |
| `doctor-dashboard.html` | Doctor's queue of routed questions |
| `question-detail.html` | Question Detail / Answer screen (doctor) |
| `profile.html` | Profile (shared) |
| `settings.html` | Settings (shared) |
| `resources.html` | Static help/resources page |

`styles.css` is shared by every page — colors, sidebar, cards, forms, buttons, badges.
Edit it once and every screen updates.

## What's real vs. placeholder

All forms are currently pointed at other pages in this folder (`action="..."`) just so
clicking "Continue" / "Submit" actually takes you somewhere during a demo. **None of them
call the real backend yet.** Each form has a comment above it noting which backend
endpoint it should eventually hit, e.g.:

```html
<!-- Wire this up to POST /uploadDocument (multipart/form-data)
     fields: username, password, caption, document(file) -->
<form id="uploadForm" action="processing.html" method="GET" enctype="multipart/form-data">
```

When the backend is ready, swap the `action` and `method` to point at the real API
(or replace the form submit with a `fetch()` call in a `<script>` tag) — the field
`name` attributes already match what `backendserver.py` expects.

The numbers, names, and matches shown on `dashboard.html`, `doctor-dashboard.html`,
and `question-detail.html` (e.g. "94% Match", "Dr. Sarah Lee") are hardcoded sample
data for the demo. Once there's an API to call, those will be replaced with real
data from the response.

## Notes

- `processing.html` auto-advances and redirects to `dashboard.html` after a few seconds —
  that's a fake animation for demo purposes only, not a real progress poll.
- The doctor sidebar shows a hardcoded "4" badge on My Queue — update this once you have
  a real count.
- Mobile responsiveness is handled at a basic level (cards stack, sidebar stays fixed-width).
  If you want the sidebar to collapse into a hamburger menu on small screens, that's the
  next thing to add.
