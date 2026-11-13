[< 013 IDEOverlays2](013-IDEOverlays2.md) | [Index](index.md) | [015 WebServers >](015-WebServers.md) <!-- nav -->

# 014 IDE Overlay Settings

**Status:** idea - no task

## Configuration Management (Project-Level)

**Master Configuration File (project.json):**
```json
{
  "name": "MyFusionProject",
  "version": "1.0.0",

  "codeQuality": {
    "invertedIfDetection": {
      "enabled": true,
      "maxNestingDepth": 3,
      "warnAtDepth": 3
    },

    "threadVisualization": {
      "enabled": true,
      "showThreadCreation": true,
      "showChannelFlow": true,
      "warnDataRaces": true
    },

    "performanceProfiling": {
      "enabled": true,
      "showInlineMetrics": true,
      "hotPathThreshold": 10
    },

    "duplicateDetection": {
      "enabled": true,
      "minSimilarity": 70,
      "minLines": 5
    },

    "namingQuality": {
      "enabled": true,
      "minNameLength": 3,
      "clarityThreshold": 50
    },

    "nestedLoops": {
      "enabled": true,
      "warnAtComplexity": "O(n²)",
      "errorAtComplexity": "O(n³)"
    },

    "controlFlowComplexity": {
      "enabled": true,
      "maxComplexity": 10,
      "maxNestingDepth": 3
    }
  }
}
```

**Per-Developer Overrides (~/.fusion/preferences.json):**
```json
{
  "codeQuality": {
    "showHints": true,
    "autoFixSuggestions": false,  // User prefers manual fixes
    "overlayOpacity": 0.7
  }
}
```

**Command-Line Overrides:**
```bash
# Disable all hints temporarily
fusion build --no-hints

# Enable only specific hints
fusion build --hints=nesting,performance

# Adjust thresholds
fusion build --max-nesting=4 --max-complexity=15
```

---

## IDE Integration Architecture

**Language Server Protocol (LSP) Extensions:**
- **Custom notifications:** Send code quality data to IDE
- **Custom commands:** "Refactor to guard clauses", "Extract function"
- **Diagnostics:** Warnings and errors for code quality issues
- **Code actions:** Quick-fixes for detected issues

**Real-time Analysis:**
- Background thread analyzes code as you type
- Non-blocking: Doesn't slow down editing
- Debounced: Waits for pause in typing before analyzing

**Visual Overlays:**
- InlayHints: Show metrics inline
- Decorations: Color overlays for heatmaps
- Gutter icons: Thread creation, hot paths
- Hover tooltips: Detailed information

---

## Benefits Summary

**For Developers:**
- ✅ Real-time code quality feedback
- ✅ Learn best practices while coding
- ✅ Catch performance issues early
- ✅ Reduce time spent in code review

**For Project Managers:**
- ✅ Enforce team coding standards automatically
- ✅ Configure quality thresholds per project
- ✅ Track code quality metrics over time
- ✅ Reduce technical debt

**For Teams:**
- ✅ Consistent code quality across team
- ✅ Faster onboarding (IDE guides new developers)
- ✅ Fewer bugs from poor practices
- ✅ Better collaboration (readable code)

---

user added comments to be formated and updated with claude
Webserver
create webserver module to handle webservices, hosting, routeing of websites
Simple host like direct index.html
Complex where its a highbrid like php where you have the weebsite.php code and inside is code to generate and add addtional sections
in code gennerateion like nodejs


above to be rechecked and checked with below
the below will not be enough to have a single additonal class
it will be under
Webserver
	- 

from chat gpt
Here’s a breakdown of **common programming languages used for web servers and hosting**, including how they compare, what they do, and where they’re used.

[< 013 IDEOverlays2](013-IDEOverlays2.md) | [Index](index.md) | [015 WebServers >](015-WebServers.md) <!-- nav -->
