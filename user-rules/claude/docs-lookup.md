# Docs lookup

Applies in every Claude Code session. For code documentation, use a documentation MCP before the editor's native web search or fetch.

Code documentation means docs for libraries, frameworks, SDKs, APIs, CLIs, and cloud services.

- Search the matching documentation MCP first. Use Microsoft Learn for Microsoft and Azure docs. Use Context7 for library, framework, SDK, and other code docs.
- When that MCP has a fetch or page tool, use it for the page you will rely on.
- If no documentation MCP applies, the call fails, or the result has nothing usable, use the editor's native web search, then its native fetch on the page you will rely on.

## Check before you state

A fact you can look up is checked before it goes into code, a doc, a ticket, or a reply.

- Provider or service behavior: the docs or schema for the provider version pinned in the repo.
- A live value (an IP, the next free name or index, PR or ticket state, what the platform already sets): query the live object.
- Who decides a value (IP allocation, naming, tags): the repo rule that owns it, cited as path:line. A value another team allocates is requested as a placeholder, never chosen.
