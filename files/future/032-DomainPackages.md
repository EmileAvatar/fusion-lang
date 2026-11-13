[< 031 Regex](031-Regex.md) | [Index](index.md) | [033 Currency >](033-Currency.md) <!-- nav -->

# 032 Domain Packages

**Status:** idea - no task (separate packages, not the core library)

## Game Engine – Separate Domain Package

**Status:** Proposed (NOT part of standard library)
**Module:** `Fusion.GameEngine` (external / community package)

Fusion should NOT ship a full game engine inside the core language because it is large, domain-specific, and opinionated.

Fusion itself only provides:

* Graphics
* Audio
* Windowing
* Input
* Shader system
* Math

A complete engine (scenes, assets, physics, ECS, animation, prefab system, etc.) belongs in a **separate ecosystem package**, not inside Core.



## Physics Library

**Status:** Proposed
**Module:** `Fusion.Physics`
**Purpose:** Physics simulation tools useful for science, engineering, robotics, and optional game development.

**Features:**

* Rigid-body physics
* Collision detection
* Forces, impulses, friction, gravity
* 2D/3D vector integration
* Raycasting utilities

**Reason:** Powerful but niche — belongs outside the core standard library.



## ECS Module (Entity Component System)

**Status:** Proposed
**Module:** `Fusion.ECS`
**Purpose:** Data-oriented architecture for high-performance simulations and optional game tooling.

**Concepts:**

* **Entity** → ID only
* **Component** → Data attached to entities
* **System** → Logic operating on all entities with matching components

**Use Cases:**

* Game engines
* Large-scale simulations
* Parallelizable workloads
* Robotics and behavior systems



## Shader Builder Tools

**Status:** Proposed
**Module:** `Fusion.Graphics.Shaders`
**Purpose:** Simplify GPU programming by providing structured tools for shader creation and validation.

**Features:**

* Vertex / Fragment / Compute shader builders
* Uniform & resource binding API
* Code generation from templates
* Syntax validation
* Cross-platform shader pipeline helpers

**Use Cases:**
Graphics, visualization, tooling, rendering pipelines.



## NumPy-Style Numerics Package

**Status:** Proposed
**Module:** `Fusion.Numerics`
**Purpose:** High-performance numeric and scientific computing.

**Features:**

* Multi-dimensional arrays
* Vectorized math
* Linear algebra (matrices, decomposition, solvers)
* FFT & numeric transforms
* Broadcasting rules

**Use Cases:**
Scientific computing, analytics, simulation, ML preprocessing.



## Pandas-Style DataFrames Package

**Status:** Proposed
**Module:** `Fusion.DataFrames`
**Purpose:** Table-based data manipulation similar to Pandas.

**Features:**

* DataFrame structure
* CSV/JSON/SQL loading
* Filtering, grouping, merging
* Sorting, aggregation
* Time-series support

**Use Cases:**
Finance, analytics, reporting, ML pipelines, ETL jobs.

[< 031 Regex](031-Regex.md) | [Index](index.md) | [033 Currency >](033-Currency.md) <!-- nav -->
