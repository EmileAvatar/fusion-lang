[< 010 IDEModule](010-IDEModule.md) | [Index](index.md) | [012 IDEOverlays >](012-IDEOverlays.md) <!-- nav -->

# 011 IDE Projects

**Status:** idea - no task (editor support: FEATURES Task 36)

**Contents**

- [IDE Module Enhancements](#ide-module-enhancements)
- [Project Integration System](#project-integration-system)

## IDE Module Enhancements

### Project Integration System

**Status:** 📝 Proposed
**Purpose:** Manage external API endpoints and data structure templates within the IDE

**What:** IDE features for importing, validating, and managing external API contracts and data schemas.

#### 1. Endpoint Management

**Purpose:** Track REST APIs, GraphQL endpoints, and service calls used by the application.

##### Features

**Import API specifications:**
- OpenAPI / Swagger JSON/YAML
- GraphQL schemas
- WSDL (SOAP services)
- Custom endpoint definitions

**Validation:**
- Ensure code calls match API contracts
- Detect type mismatches in request/response
- Warn about deprecated endpoints

🧩 **Example:**
```fusion
// Import API specification
import fusionlib.IDE

// Load OpenAPI spec
APISpec spec = ProjectIntegration.loadOpenAPI("./api/petstore.yaml")

// IDE validates this call against spec
void function fetchUser(int userId)
    // IDE knows this endpoint exists and requires int parameter
    HttpResponse response = Http.get("https://api.example.com/users/{userId}")

    // IDE validates response structure matches spec
    User user = response.parseJson<User>()
```

##### IDE Features

**Auto-complete endpoints:**
```fusion
Http.get("https://api.example.com/")
// IDE suggests: /users, /products, /orders (from imported spec)
```

**Endpoint browser panel:**
```
📁 Project Endpoints
  └─ 🌐 PetStore API (https://api.petstore.com)
      ├─ GET /pets
      ├─ POST /pets
      ├─ GET /pets/{id}
      └─ DELETE /pets/{id}
```

**Generate client code:**
```fusion
// IDE generates client class from OpenAPI spec
class PetStoreClient
    List<Pet> function getPets()
    Pet function getPet(int id)
    void function createPet(Pet pet)
    void function deletePet(int id)
```

#### 2. Data Structure Templates

**Purpose:** Manage JSON schemas, XML templates, database schemas, and data format contracts.

##### Supported Formats

- JSON Schema
- XML Schema (XSD)
- Database schemas (SQL DDL, ER diagrams)
- CSV column definitions
- Protocol buffers (.proto files)
- Avro schemas

🧩 **Example: JSON Schema Validation**

**Import schema:**
```json
// schemas/user.json
{
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "name": { "type": "string", "minLength": 1 },
    "email": { "type": "string", "format": "email" },
    "age": { "type": "integer", "minimum": 0, "maximum": 150 }
  },
  "required": ["id", "name", "email"]
}
```

**IDE integration:**
```fusion
import fusionlib.IDE

// Register schema
ProjectIntegration.registerSchema("User", "./schemas/user.json")

// IDE validates this class matches schema
class User
    int id
    string name
    string email
    int age  // IDE warns if type doesn't match schema

// IDE validates JSON parsing
string json = """{"id": 1, "name": "Alice", "email": "alice@example.com"}"""
User user = Json.parse<User>(json)  // IDE checks structure
```

#### 3. Template Library

**Purpose:** Store and reuse data format templates directly in code.

##### Store Templates as Comments

```fusion
/**
 * @template UserJSON
 * {
 *   "id": 0,
 *   "name": "",
 *   "email": "",
 *   "roles": []
 * }
 */

/**
 * @template ConfigXML
 * <config>
 *   <database>
 *     <host>localhost</host>
 *     <port>5432</port>
 *     <name>mydb</name>
 *   </database>
 * </config>
 */
```

##### IDE Features

**Insert template at cursor:**
```
Right-click → Insert Template → UserJSON
// Pastes template into code
```

**View template in sidebar:**
```
📁 Templates
  ├─ 📄 UserJSON
  ├─ 📄 ConfigXML
  └─ 📄 OrderRequest
```

**Validate against template:**
```fusion
// IDE compares this JSON to @template UserJSON
string userJson = """
{
  "id": 123,
  "name": "Bob"
  // ⚠️  Warning: Missing required field "email"
}
"""
```

#### 4. Database Schema Integration

**Purpose:** Import database schemas and generate model classes.

🧩 **Example:**
```fusion
import fusionlib.IDE

// Import database schema
DatabaseSchema schema = ProjectIntegration.importDatabaseSchema(
    "postgresql://localhost:5432/mydb"
)

// IDE generates classes from tables
// Auto-generated from 'users' table:
class UserModel
    int id          // PRIMARY KEY
    string name     // VARCHAR(100) NOT NULL
    string email    // VARCHAR(255) UNIQUE
    DateTime created // TIMESTAMP DEFAULT NOW()
```

**IDE validation:**
```fusion
// IDE warns if query doesn't match schema
string sql = "SELECT id, name, invalid_column FROM users"
// ⚠️  Warning: Column 'invalid_column' does not exist in table 'users'
```

#### 5. ProjectIntegration API

```fusion
// Module: fusionlib.IDE

class ProjectIntegration
    // === API Endpoints ===
    static APISpec loadOpenAPI(string path)
    static APISpec loadGraphQL(string path)
    static void registerEndpoint(string name, string url, HttpMethod method)
    static List<Endpoint> getAllEndpoints()

    // === Data Schemas ===
    static void registerSchema(string name, string schemaPath)
    static Schema getSchema(string name)
    static bool validateAgainstSchema(object data, string schemaName)
    static void generateClassFromSchema(string schemaName, string outputPath)

    // === Templates ===
    static void registerTemplate(string name, string content)
    static string getTemplate(string name)
    static List<Template> getAllTemplates()

    // === Database Integration ===
    static DatabaseSchema importDatabaseSchema(string connectionString)
    static void generateModelsFromDatabase(string connectionString, string outputPath)
    static void validateQuery(string sql, string databaseName)

Enum HttpMethod { GET, POST, PUT, DELETE, PATCH }

class Endpoint
    string name
    string url
    HttpMethod method
    Schema requestSchema
    Schema responseSchema

class Schema
    string name
    string format  // "json", "xml", "csv", etc.
    string content
    bool function validate(object data)

class Template
    string name
    string content
    string description
```

[< 010 IDEModule](010-IDEModule.md) | [Index](index.md) | [012 IDEOverlays >](012-IDEOverlays.md) <!-- nav -->
