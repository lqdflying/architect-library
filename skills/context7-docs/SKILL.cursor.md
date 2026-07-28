---
name: context7-docs
description: Fetch current library, framework, SDK, API, or CLI documentation via the Context7 MCP server instead of relying on training data. Use when the user asks about libraries, frameworks, API references, setup, configuration, version migration, library-specific debugging, or CLI tool usage. Activates for mentions of specific libraries like React, Next.js, Prisma, Express, Tailwind, Django, Terraform providers, etc.
---

# Fetch Library and Framework Documentation (Context7)

Use the **Context7 MCP server** (`user-context7`) to fetch current, accurate documentation for any library, framework, SDK, API, or CLI tool. Training data may be outdated — always verify against live docs.

## When to Use

Activate this skill when the user:

- Asks setup or configuration questions ("How do I configure Next.js middleware?")
- Requests code involving libraries ("Write a Prisma query for...")
- Needs API references ("What are the Supabase auth methods?")
- Mentions specific frameworks or libraries (React, Vue, Svelte, Express, Tailwind, Django, Flask, Spring Boot, etc.)
- Asks about version migration ("What changed in React 19?")
- Debugs library-specific behavior ("Why does useEffect fire twice?")
- Needs CLI tool usage ("How do I use the Terraform CLI import command?")
- References Terraform providers (AzureRM, AWS, GCP, Databricks, Kubernetes)

## When NOT to Use

Do not activate for:

- General programming concepts (algorithms, data structures, design patterns)
- Refactoring or writing scripts from scratch with no library dependency
- Debugging business logic unrelated to a library
- Code review (use the code-review agent instead)

## Workflow

### Step 1: Resolve the Library ID

If the user already provides a Context7 library ID in `/org/project` or `/org/project/version` format (e.g. `/vercel/next.js`, `/facebook/react/v19.0.0`), skip resolution and go directly to Step 3.

Otherwise, call `resolve-library-id` on the `user-context7` MCP server:

```
GetMcpTools({ server: "user-context7" })

CallMcpTool({
  server: "user-context7",
  toolName: "resolve-library-id",
  arguments: {
    libraryName: "Next.js",
    query: "How do I configure middleware in Next.js 15?"
  }
})
```

- `libraryName`: the official library name with proper punctuation (e.g. "Next.js" not "nextjs", "Three.js" not "threejs")
- `query`: the user's full question — improves relevance ranking

### Step 2: Select the Best Match

From the resolution results, choose based on:

- **Name match**: exact or closest match to what the user asked for
- **Source reputation**: prefer High or Medium reputation sources
- **Benchmark score**: higher scores indicate better documentation quality
- **Code snippets**: higher counts mean more practical examples available
- **Version**: if the user mentioned a version (e.g. "React 19", "Next.js 15"), prefer version-specific IDs (format: `/org/project/version`)

If multiple good matches exist, proceed with the most relevant one. If no good matches exist, say so and suggest query refinements.

### Step 3: Query the Documentation

Call `query-docs` with the selected library ID:

```
CallMcpTool({
  server: "user-context7",
  toolName: "query-docs",
  arguments: {
    libraryId: "/vercel/next.js",
    query: "How to configure middleware"
  }
})
```

- `libraryId`: the Context7-compatible ID from Step 2 (e.g. `/vercel/next.js`)
- `query`: a specific, focused question scoped to a single concept

**Query decomposition**: if the user's question spans multiple distinct concepts, make a separate `query-docs` call per concept rather than combining them into one broad query. Exception: when the question is about how concepts interact, a single call is fine.

Good queries:
- "How to set up authentication with JWT in Express.js"
- "React useEffect cleanup function examples"

Bad queries:
- "auth" (too vague)
- "routing and auth and caching in Next.js" (too broad — split into separate calls)

### Step 4: Use the Documentation

Incorporate the fetched documentation into your response:

- Answer the user's question using current, accurate information from the docs
- Include relevant code examples from the docs
- Cite the library version when relevant
- Include source URLs when the docs provide them

## Limits

- Do not call `resolve-library-id` more than **3 times** per user question
- Do not call `query-docs` more than **3 times** per user question
- If you cannot find what you need after 3 resolution attempts, use the best result you have

## Fallback

If Context7 does not have documentation for a library:

1. Try alternative library names or official package names
2. Fall back to **web search** (`WebSearch` or `user-tavily`) for the library's official docs
3. For Azure/Microsoft libraries, use **Microsoft Learn MCP** (`user-microsoftdocs`) instead
4. State clearly when you are using training-data knowledge instead of verified docs

## Guidelines

- **Be specific**: pass the user's full question as the query for better results
- **Version awareness**: when users mention versions ("Next.js 15", "React 19"), use version-specific library IDs if available from the resolution step. Version-pinned IDs use the format `/org/project/version` (e.g. `/vercel/next.js/v15.1.8`, `/facebook/react/v19.0.0`)
- **Direct ID shortcut**: if the user provides a library ID starting with `/`, skip `resolve-library-id` and call `query-docs` directly
- **Prefer official sources**: when multiple matches exist, prefer official/primary packages over community forks
- **Do not fabricate**: if docs do not cover the user's question, say so rather than guessing
- **Cite sources**: include the library name, version, and source URL in responses when the docs provide them
