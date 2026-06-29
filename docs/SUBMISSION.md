# SCHOLY - Submission material

## Project Description (English, for Kaggle)

**SCHOLY — Your multi-agent scholarship advisor**

Finding the right scholarship is slow, scattered, and confusing. Information lives
across hundreds of sites, every program has different rules (level, language,
nationality, GPA), and—worst of all—a scholarship you "find" isn't always
*viable*: many cover only tuition and leave housing, food, and transport
unfunded in a foreign country.

SCHOLY solves this with a **team of specialized AI agents** built on the **Google
Agent Development Kit (ADK)**. Instead of one prompt doing everything, four agents
work as an assembly line: a **ProfileAgent** structures the student's profile, a
**SearchAgent** finds real scholarships on the web via grounded Google Search, an
**EligibilityAgent** filters by eligibility and scores each match with a
deterministic tool, and an **AdvisorAgent** delivers a ranked recommendation with
a clear **financial-fit analysis**.

The result is served through a clean, responsive FastAPI + web UI. Built with
security first: **zero API keys in code**, layered **prompt-injection guardrails**,
and full **observability** through ADK plugins.

SCHOLY doesn't just find scholarships—it tells students which ones they can
actually win and afford.

---

## Project Links

- **GitHub repository:** <pega-aquí-tu-URL-de-GitHub>
- **YouTube video (pitch/demo):** <pendiente>

---

## Course concepts demonstrated (rubric mapping)

- **Multi-agent system (ADK):** four specialized agents orchestrated as a
  `SequentialAgent` (`scholy/agent.py`).
- **MCP Server:** optional external-search connector via `McpToolset`
  (`scholy/tools/search_mcp.py`, V2 path).
- **Security features:** zero API keys in code (`.env` + `.gitignore`), two-layer
  prompt-injection defense (`scholy/security/`), frontend XSS escaping.
- **Tools / Agent skills:** built-in `google_search` + a deterministic
  compatibility-scoring `FunctionTool` (`scholy/tools/scholarship_tools.py`).
- **Observability (Agent Ops):** `LoggingPlugin` + custom `CountInvocationPlugin`
  (`scholy/observability.py`).
- **Deployability:** documented Cloud Run guide in the README (not deployed live
  due to no GCP billing; deployment is optional per the rubric).
