# AI Declaration step (I01)

This step carries no computation. It exists so the project's AI usage
declaration is a first-class, verifiable part of the pipeline rather
than a loose file.

The declaration itself lives at the repository root in
[`AI_USAGE.md`](../AI_USAGE.md); this step points at it.

The step is interactive: only the researcher's own sign-off can pass
it. No agent can attest to its own declaration.
