Northbeam Docs Studio — Tasks
- [ ] 1. Finalize planning: Review the feature rules, adopt these drafts through Spec Kit's specify → plan → tasks workflow, and commit the planning artifacts before application code.
- [ ] 2. Set up the project: Create Vue 3 and Flask applications, dependencies, SQLite initialization and constraints, and a repeatable local startup process.
- [ ] 3. Build the API: Implement draft creation/editing, atomic publish, unpublish, public reading, and stale-request rejection using revisions.
- [ ] 4. Add version management: Implement newest-first history, snapshot inspection, non-destructive restore, and API/database protection against deleting the referenced snapshot.
- [ ] 5. Build the Vue pages: Add the writer list/editor, safe Markdown preview, publish controls, history actions, public pages, and clear conflict/404 messages.
- [ ] 6. Test and document: Verify lifecycle rules, rollback, concurrency, and persistence; provide one test command and README setup/model/tradeoff notes; check a clean checkout and preserve spec-before-code Git history.