# Common Agent Swarm Operation System CASOPS

This boilerplate establishes CASOPS through a spec-driven development (SDD) process. Execute the following sequence without reordering it.

## Agent boundary

Create and synchronize configuration only for **Kiro** and **Claude Code**. Do not generate, adapt, install, migrate, synchronize, or otherwise configure any other agent or tool.

Gemini and Gemini CLI are permanently excluded: never collect, download, inspect for reuse, curate, migrate, synchronize, or generate any Gemini or Gemini CLI skill, configuration, rule, command, agent, or related artifact. Ignore any Gemini-related material encountered in source documents.

## Implementation sequence

1. Review `starter.md` to understand only the structural requirements, workflows, and baseline specifications applicable to CASOPS, Kiro, and Claude Code.
2. Set up the core CASOPS infrastructure from `starter.md`, including the directory hierarchy, baseline dependencies, and only Kiro and Claude Code configuration.
3. Migrate the applicable content, guidelines, and technical requirements from `sdd_framework.md` into the CASOPS structure; exclude all unsupported-agent material and all Gemini/Gemini CLI material.
4. Implement lifecycle-wide SDD enforcement:
   - pre-commit checks that block commits lacking validated specifications;
   - CI/CD checks that verify specification completeness and code alignment before builds or deployments;
   - templates that create required specifications for every feature, module, or code change; and
   - validation tools that cross-reference specifications and implemented behavior.
5. Verify the enforcement mechanisms from feature planning through submission, review, and deployment.
6. Confirm the completed CASOPS setup complies with the applicable requirements in `starter.md` and `sdd_framework.md`, operates only with Kiro and Claude Code configuration, and enforces SDD as the required methodology.
