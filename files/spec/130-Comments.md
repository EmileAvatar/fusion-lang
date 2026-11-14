[< 120 Errors](120-Errors.md) | [Index](index.md) | [131 AutoDocs >](131-AutoDocs.md) <!-- nav -->

# 130 Comments

**Contents**

- [Single-Line Comments](#single-line-comments)
- [Multi-Line Comments](#multi-line-comments)
- [Region Blocks](#region-blocks)
- [Documentation Comments](#documentation-comments)

## Comments and Code Organization

**Status:** [PARTLY] `//` and `/* */` comments are built (01-04, SYN.029); `'` comments postponed (SYN.031);
region blocks and documentation comments designed (SYN.032); `'''` comment blocks and comment levels designed (SYN.036)

Description: Code documentation and organizational features.

---

### Single-Line Comments

Description: Two comment styles based on user preference.

* **Double Slash** (Stored as `//` in Fusion)

```
// This is a single-line comment
int count = 10  // End-of-line comment

// Multiple single-line comments
// can be used for longer
// explanations
```

* **Single Quote** (VB style) - **postponed** (SYN.031): off, so that a char literal `'c'` works; maybe only
  at the start of a line

```
' This is a single-line comment
int count = 10  ' End-of-line comment

' Multiple single-line comments
' using single quotes
```

**Note** (once `'` comments are on):
- Both styles work the same
- Fusion stores every comment as `//`
- The editor shows the style the developer prefers

---

### Multi-Line Comments

Description: Block comments spanning multiple lines.

```
/* 
 * This is a multi-line comment
 * Spanning multiple lines
 * Useful for longer explanations
 */

void function processData(Data data)
    /* Quick inline multi-line comment */
    data.process()

/*
 * Function: calculateDistance
 * Parameters:
 *   - x1, y1: First point
 *   - x2, y2: Second point
 * Returns: Distance between points
 */
float function calculateDistance(float x1, float y1, float x2, float y2)
    float dx = x2 - x1
    float dy = y2 - y1
    return sqrt(dx * dx + dy * dy)
```

---

### Region Blocks

Description: Collapsible code sections for IDE organization.

* **Purpose**: Organize large files into logical sections
* **IDE Support**: Regions can be collapsed/expanded in IDE
* **No Runtime Effect**: Pure organizational feature

```
#Region Initialization Code
void function initialize()
    setupSystem()
    loadConfiguration()
    connectDatabase()

void function setupSystem()
    // System setup code
#End Region

#Region Helper Functions
void function helper1()
    // Helper implementation

void function helper2()
    // Helper implementation

private void function internalHelper()
    // Internal helper
#End Region

#Region Data Structures
class DataCache
    // Cache implementation

struct CacheEntry
    string key
    string value
#End Region
```

**Features**:
* String literal displays in IDE when collapsed
* Can nest regions
* Helps navigate large files
* No effect on compilation
* IDE shows as: `[+] Initialization Code`

---

### Documentation Comments

Description: Special comments for API documentation generation - read by the documentation
generator ([131 AutoDocs](131-AutoDocs.md)). Designed (SYN.032).

```
/**
 * Calculates the distance between two points in 2D space.
 * 
 * @param x1 X coordinate of first point
 * @param y1 Y coordinate of first point
 * @param x2 X coordinate of second point
 * @param y2 Y coordinate of second point
 * @return Distance between the points
 * @example
 *   float dist = calculateDistance(0, 0, 3, 4)  // Returns 5.0
 */
float function calculateDistance(float x1, float y1, float x2, float y2)
    float dx = x2 - x1
    float dy = y2 - y1
    return sqrt(dx * dx + dy * dy)
```

[< 120 Errors](120-Errors.md) | [Index](index.md) | [131 AutoDocs >](131-AutoDocs.md) <!-- nav -->
