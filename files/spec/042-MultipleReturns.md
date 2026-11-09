[< 041 Lambdas](041-Lambdas.md) | [Index](index.md) <!-- nav -->

# 042 MultipleReturns

## Error Handling with Multiple Returns

**Status:** [PLANNED 26]

Description: Go-style multiple return values for explicit error handling.

* **Function with Error Return**

```
Spaceship, Error function loadShip(string filename)
    if not fileExists(filename)
        return null, Error("File not found: {filename}")
    
    Spaceship ship = parseShipFile(filename)
    if ship is null
        return null, Error("Invalid ship data")
    
    return ship  // Success - error is implicitly null
```

* **Calling with Error Capture**

```
Spaceship ship, Error err = loadShip("ship.dat")

// Check error first
if err
    print("Error loading ship: {err.message}")
    return

// Safe to use ship (no error occurred)
ship.start()
```

* **Calling Without Error Capture** (Bubble up)

```
// Error bubbles up to caller if it occurs
Spaceship ship = loadShip("ship.dat")
ship.start()
```

* **Error Object**

```
class Error
    string message
    int code
    string stackTrace
    
    constructor(string msg)
        this.message = msg
        this.code = 0
        this.stackTrace = captureStackTrace()
```

* **Error Chaining**

```
Spaceship, Error function loadAndValidateShip(string filename)
    Spaceship ship, Error err = loadShip(filename)
    if err
        return null, err
    
    bool valid, Error err2 = validateShip(ship)
    if err2
        return null, err2
    
    return ship
```

[< 041 Lambdas](041-Lambdas.md) | [Index](index.md) <!-- nav -->
