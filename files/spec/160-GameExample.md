[< 150 Modules](150-Modules.md) | [Index](index.md) | [170 Build >](170-Build.md) <!-- nav -->

# 160 Game Example

## Complete Game Example

**Status:** [DESIGN] shows the full intended language - partly built: structs, classes, interfaces,
constructors, Lists built (Tasks 18, 32); properties `{ get; set; }` designed (CLS.011); `module SpaceGame`
is the earlier design - a module is a folder ([150 Modules](150-Modules.md))

Description: Putting it all together in a simple space game using Fusion v2 syntax.

```
// game.fusion - Complete space game example
module SpaceGame

// Vector math structure - a plain value type (functions inside a struct: [structs] functions, 32.1)
struct Vector2
    float x
    float y

// Vector math lives in ordinary functions
Vector2 function vadd(Vector2 a, Vector2 b)
    return Vector2(a.x + b.x, a.y + b.y)

Vector2 function vscale(Vector2 v, float scalar)
    return Vector2(v.x * scalar, v.y * scalar)

// Base game object interface
interface GameObject
    property Position: Vector2 { get; set; }
    void function update(float deltaTime)
    void function render()

// Spaceship class
class Spaceship implements GameObject
    property Position: Vector2 { get; set; }
    property Velocity: Vector2 { get; set; }
    property Health: float { get; set; }
    property Name: string { get; private set; }
    
    private float fuel
    private bool isActive
    
    constructor(string name, Vector2 startPos)
        this.Name = name
        this.Position = startPos
        this.Velocity = Vector2(0, 0)
        this.Health = 100.0
        this.fuel = 100.0
        this.isActive = true
    
    void function accelerate(Vector2 direction, float power)
        if fuel > 0 and isActive
            Velocity = vadd(Velocity, vscale(direction, power))
            fuel -= power * 0.1
    
    void function update(float deltaTime)
        if isActive
            Position = vadd(Position, vscale(Velocity, deltaTime))

            // Apply drag
            Velocity = vscale(Velocity, 0.99)
            
            // Regenerate fuel slowly
            if fuel < 100
                fuel += deltaTime * 2.0
        end loop
    
    void function render()
        if isActive
            drawSprite("ship", Position.x, Position.y)
            drawHealthBar(Position.x, Position.y - 20, Health)
    
    void function takeDamage(float amount)
        Health -= amount
        if Health <= 0
            Health = 0
            isActive = false
            print("{Name} destroyed!")

// Projectile class
class Projectile implements GameObject
    property Position: Vector2 { get; set; }
    property Velocity: Vector2 { get; set; }
    property Damage: float { get; private set; }
    
    private float lifetime
    private float maxLifetime = 3.0
    
    constructor(Vector2 startPos, Vector2 velocity, float damage)
        this.Position = startPos
        this.Velocity = velocity
        this.Damage = damage
        this.lifetime = 0
    
    void function update(float deltaTime)
        Position = vadd(Position, vscale(Velocity, deltaTime))
        lifetime += deltaTime
    
    void function render()
        if lifetime < maxLifetime
            drawCircle(Position.x, Position.y, 3, Color.Yellow)
    
    property IsExpired: bool
        get
            return lifetime >= maxLifetime

// Game manager class
class GameManager
    private List<Spaceship> ships
    private List<Projectile> projectiles
    private float gameTime
    private bool isRunning
    
    constructor()
        ships = List<Spaceship>()
        projectiles = List<Projectile>()
        gameTime = 0
        isRunning = false
    
    void function initialize()
        // Create player ship
        Spaceship player = Spaceship("Player", Vector2(400, 300))
        ships.append(player)
        
        // Create enemy ships
        for i in range(5)
            Vector2 enemyPos = Vector2(100 + i * 150, 100)
            Spaceship enemy = Spaceship("Enemy-{i}", enemyPos)
            ships.append(enemy)
        end loop
        
        isRunning = true
        print("Game initialized with {ships.Count} ships")
    
    void function update(float deltaTime)
        if not isRunning
            return
        
        gameTime += deltaTime
        
        // Update all ships
        for ship in ships
            ship.update(deltaTime)
        end loop
        
        // Update projectiles
        for projectile in projectiles
            projectile.update(deltaTime)
        end loop
        
        // Remove expired projectiles
        projectiles = projectiles.filter(lambda p: not p.IsExpired)
        
        // Check collisions
        checkCollisions()
        
        // Remove destroyed ships
        ships = ships.filter(lambda s: s.Health > 0)
        
        // Check win/lose conditions
        if ships.Count == 1
            print("Victory! Time: {gameTime} seconds")
            isRunning = false
    
    void function render()
        clearScreen()
        
        for ship in ships
            ship.render()
        end loop
        
        for projectile in projectiles
            projectile.render()
        end loop
        
        drawText("Ships: {ships.Count}", 10, 10)
        drawText("Time: {gameTime}", 10, 30)
    
    void function fireProjectile(Spaceship fromShip, Vector2 direction)
        Projectile projectile = Projectile(
            fromShip.Position,
            vscale(direction, 500.0),
            25.0
        )
        projectiles.append(projectile)
    
    private void function checkCollisions()
        for projectile in projectiles
            for ship in ships
                float dx = ship.Position.x - projectile.Position.x
                float dy = ship.Position.y - projectile.Position.y
                float distance = dx * dx + dy * dy
                
                if distance < 400  // 20 pixel radius squared
                    ship.takeDamage(projectile.Damage)
                    projectile.lifetime = projectile.maxLifetime
            end loop
        end loop

// Main game loop
void function main()
    GameManager game = GameManager()
    game.initialize()
    
    float lastTime = getTime()
    
    while game.isRunning
        float currentTime = getTime()
        float deltaTime = currentTime - lastTime
        lastTime = currentTime
        
        // Handle input
        if isKeyPressed(Key.Space)
            Spaceship player = game.ships[0]
            game.fireProjectile(player, Vector2(0, -1))
        
        if isKeyDown(Key.Left)
            game.ships[0].accelerate(Vector2(-1, 0), 10.0)
        
        if isKeyDown(Key.Right)
            game.ships[0].accelerate(Vector2(1, 0), 10.0)
        
        // Update and render
        game.update(deltaTime)
        game.render()
        
        // Cap framerate
        sleep(16)  // ~60 FPS
    end loop
```

[< 150 Modules](150-Modules.md) | [Index](index.md) | [170 Build >](170-Build.md) <!-- nav -->
