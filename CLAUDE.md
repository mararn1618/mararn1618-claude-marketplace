# Claude Marketplace

This repo contains Claude Code plugins (skills).

## Structure

```
<plugin-name>/
  .claude-plugin/plugin.json   # Plugin metadata + version
  skills/<skill-name>/SKILL.md # Skill definitions
.claude-plugin/marketplace.json # Registry of all plugins + versions
```

## Versioning

When updating a plugin, bump the version in **both** places:
1. `<plugin-name>/.claude-plugin/plugin.json` (`"version"`)
2. `.claude-plugin/marketplace.json` (matching entry's `"version"`)

Both versions must always match. Use semver (major.minor.patch).
