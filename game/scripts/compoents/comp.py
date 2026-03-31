import engine

@engine.components.component
class Player:
    pass

@engine.components.component
class PlayerConfig:
    strength: float
    power_inc: float
    max_strength: float
    friction: float
    shoot_timer: float
    max_shoot_time: float
    invulnerable: float
    max_invul_time: float

@engine.components.component
class PlayerShoot:
    pass

@engine.components.component
class CollTile:
    pass

@engine.components.component
class PlayerBullet:
    pass

@engine.components.component
class EnemyShooter:
    pass

@engine.components.component
class EnemyDefender:
    pass

@engine.components.component
class EnemyDasher:
    pass

@engine.components.component
class EnemySpawn:
    spawn_timer: float
    max_spawn_time: float