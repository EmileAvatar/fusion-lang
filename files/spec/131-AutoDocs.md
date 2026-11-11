[< 130 Comments](130-Comments.md) | [Index](index.md) | [140 Collections >](140-Collections.md) <!-- nav -->

# 131 AutoDocs

## Auto-Documentation

**Status:** [DESIGN] no task yet (SYN.032) - documentation comments themselves: [130 Comments](130-Comments.md)

Description: Generate documentation from source comments.

**Documentation Format**:
```
/**
 * @title Spaceship Class
 * @description Main spaceship entity
 * @category Game/Entities
 * @example
 *   Spaceship ship = Spaceship("Enterprise", 100.0)
 */
class Spaceship
```

**Generate**:
```bash
fusion doc generate --output ./wiki
```

[< 130 Comments](130-Comments.md) | [Index](index.md) | [140 Collections >](140-Collections.md) <!-- nav -->
