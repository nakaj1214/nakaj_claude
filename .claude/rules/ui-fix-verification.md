# UI Fix Verification Rules

## Read Requirements Literally

When reading `proposal.md` or bug reports in Japanese:

- "〜が存在している" = remove it
- "文字がない" = add the text
- "中央になってない" = add `vertical-align: middle` or equivalent
- "大きさが違う" = unify padding/height/font-size

**Start with the simplest possible fix.** Only investigate deeper if the simple fix doesn't work.

If a fix should take less than 5 minutes but you're spending longer, re-read the requirement — the interpretation is likely wrong.

"改善されていない（N回目）" means **you misread the requirement**, not that the problem is complex.

## Verify Execution Paths After UI Changes

After modifying frontend code, trace these before marking complete:

### Event Handlers
- Does the jQuery selector actually match the DOM? (e.g. `a[data-bs-toggle="tab"]` vs `div.tab[data-tab]`)
- Is the event delegated to a parent that exists at bind time?

### Async Operations
- Does `ajax.reload()` have a callback for post-reload work?
- Is scroll restoration called AFTER data rendering completes?

### CSS Overrides
- Check ALL properties injected by JS (not just `background` — also `box-shadow`, `outline`, `border`)
- Use `#id` selectors to beat `!important` from injected styles

### User Flow Simulation
- Trace the full user flow: login → action → logout → re-login
- Check if cleanup logic (e.g. localStorage deletion) conflicts with save logic

### This Project's Custom Components
- Tabs: `<div class="tab" data-tab="...">` — NOT Bootstrap `<a data-bs-toggle="tab">`
- DataTables Scroller: use `scroller.toPosition(rowIndex)` — NOT `scrollTop(px)`
