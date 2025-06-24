class Character {
  constructor(scene, config) {
    this.scene = scene;
    this.id = config.id;
    this.name = config.name;
    this.spawnPoint = config.spawnPoint;
    this.atlas = config.atlas;
    
    // Map new character IDs to their actual atlas frame prefixes
    this.framePrefix = this.getFramePrefix(this.id);
    this.defaultFrame = `${this.framePrefix}-${config.defaultDirection || 'front'}`;
    this.defaultMessage = config.defaultMessage;
    
    this.isRoaming = config.canRoam !== false; 
    this.moveSpeed = config.moveSpeed || 20;
    this.movementTimer = null;
    this.currentDirection = null;
    this.moveDuration = 0;
    this.pauseDuration = 0;
    this.roamRadius = config.roamRadius || 200; 
    this.pauseChance = config.pauseChance || 0.2; 
    this.directionChangeChance = config.directionChangeChance || 0.3;

    this.sprite = this.scene.physics.add
      .sprite(this.spawnPoint.x, this.spawnPoint.y, this.atlas, this.defaultFrame)
      .setSize(30, 40)
      .setOffset(0, 0)
      .setImmovable(true);

    this.scene.physics.add.collider(this.sprite, config.worldLayer);
    
    this.createAnimations();
    this.createNameLabel();
    
    if (this.isRoaming) {
      this.startRoaming();
    }
  }
  
  /**
   * Maps character IDs to their corresponding asset folder names.
   * This handles cases where the character ID used in game logic 
   * differs from the actual asset folder name.
   * 
   * @param {string} characterId - The character ID used in game configuration
   * @returns {string} The corresponding asset folder name/frame prefix
   * @throws {Error} If character ID is invalid
   * 
   * @example
   * getFramePrefix('messi') // returns 'leomessi'
   * getFramePrefix('ronaldo') // returns 'cristianoronaldo'
   * getFramePrefix('kaka') // returns 'kaka'
   */
  getFramePrefix(characterId) {
    // Validate input
    if (!characterId || typeof characterId !== 'string') {
      throw new Error(`Invalid character ID: ${characterId}. Expected non-empty string.`);
    }

    // Character ID to asset folder mapping (Centralized configuration)
    const CHARACTER_ASSET_MAPPING = Object.freeze({
      // Characters with different asset folder names
      'messi': 'leomessi',
      'ronaldo': 'cristianoronaldo',
      
      // Characters with matching asset folder names
      'ronaldonazario': 'ronaldonazario',
      'kaka': 'kaka',
      'maradona': 'maradona',
      'neymar': 'neymar',
      'sergioramos': 'sergioramos',
      'pepguardiola': 'pepguardiola',
      'alexferguson': 'alexferguson',
      'ancelotti': 'ancelotti',
      'jurgenklopp': 'jurgenklopp',
      'sophia': 'sophia'
    });

    const normalizedId = characterId.toLowerCase().trim();
    const assetName = CHARACTER_ASSET_MAPPING[normalizedId];
    
    if (!assetName) {
      // Enhanced debugging with stack trace context
      console.warn(`[Character] Asset mapping not found for ID: "${characterId}". Available IDs: ${Object.keys(CHARACTER_ASSET_MAPPING).join(', ')}. Using normalized ID as fallback: "${normalizedId}"`);
      return normalizedId;
    }

    return assetName;
  }

  /**
   * Validates if a frame exists in the loaded texture atlas
   * @param {string} frameName - The frame name to validate
   * @returns {boolean} True if frame exists, false otherwise
   */
  validateFrame(frameName) {
    try {
      const texture = this.scene.textures.get(this.atlas);
      return texture && texture.has(frameName);
    } catch (error) {
      console.warn(`[Character] Frame validation failed for "${frameName}":`, error.message);
      return false;
    }
  }
  
  /**
   * Creates walking animations for all directions.
   * Uses framePrefix for proper asset mapping and includes error handling.
   */
  createAnimations() {
    const anims = this.scene.anims;
    const directions = ['left', 'right', 'front', 'back'];
    
    directions.forEach(direction => {
      const animKey = `${this.id}-${direction}-walk`;
      
      if (!anims.exists(animKey)) {
        try {
          // Validate that at least the first frame exists before creating animation
          const firstFrameName = `${this.framePrefix}-${direction}-walk-0000`;
          
          if (!this.validateFrame(firstFrameName)) {
            console.warn(`[Character] Missing animation frames for ${this.id} (${this.framePrefix}) direction: ${direction}. Skipping animation creation.`);
            return;
          }

          anims.create({
            key: animKey,
            frames: anims.generateFrameNames(this.atlas, {
              prefix: `${this.framePrefix}-${direction}-walk-`,
              end: 8,
              zeroPad: 4,
            }),
            frameRate: 10,
            repeat: -1,
          });
        } catch (error) {
          console.error(`[Character] Failed to create animation for ${this.id} direction ${direction}:`, error);
        }
      }
    });
  }
  
  facePlayer(player) {
    const dx = player.x - this.sprite.x;
    const dy = player.y - this.sprite.y;
    
    if (Math.abs(dx) > Math.abs(dy)) {
      this.sprite.setTexture(this.atlas, `${this.framePrefix}-${dx < 0 ? 'left' : 'right'}`);
    } else {
      this.sprite.setTexture(this.atlas, `${this.framePrefix}-${dy < 0 ? 'back' : 'front'}`);
    }
  }
  
  distanceToPlayer(player) {
    return Phaser.Math.Distance.Between(
      player.x, player.y,
      this.sprite.x, this.sprite.y
    );
  }
  
  isPlayerNearby(player, distance = 55) {
    return this.distanceToPlayer(player) < distance;
  }
  
  startRoaming() {
    this.chooseNewDirection();
  }
  
  chooseNewDirection() {
    if (this.movementTimer) {
      this.scene.time.removeEvent(this.movementTimer);
    }
    
    if (Math.random() < 0.4) { 
      const directions = ['left', 'right', 'up', 'down'];
      this.currentDirection = directions[Math.floor(Math.random() * directions.length)];
      
      const animKey = `${this.id}-${this.getDirectionFromMovement()}-walk`;
      if (this.scene.anims.exists(animKey)) {
        this.sprite.anims.play(animKey);
      } else {
        this.sprite.setTexture(this.atlas, `${this.framePrefix}-${this.getDirectionFromMovement()}`);
      }
      
      this.moveDuration = Phaser.Math.Between(500, 1000);
      this.movementTimer = this.scene.time.delayedCall(this.moveDuration, () => {
        this.sprite.body.setVelocity(0);
        this.chooseNewDirection();
      });
    } else {
      this.currentDirection = null;
      this.sprite.anims.stop();
      
      const direction = ['front', 'back', 'left', 'right'][Math.floor(Math.random() * 4)];
      this.sprite.setTexture(this.atlas, `${this.framePrefix}-${direction}`);
      
      this.pauseDuration = Phaser.Math.Between(2000, 6000);
      this.movementTimer = this.scene.time.delayedCall(this.pauseDuration, () => {
        this.chooseNewDirection();
      });
    }
  }
  
  getDirectionFromMovement() {
    switch(this.currentDirection) {
      case 'left': return 'left';
      case 'right': return 'right';
      case 'up': return 'back';
      case 'down': return 'front';
      default: return 'front';
    }
  }
  
  moveInCurrentDirection() {
    if (!this.currentDirection) return;
    
    const previousPosition = { x: this.sprite.x, y: this.sprite.y };
    
    this.sprite.body.setVelocity(0, 0); 
    
    switch(this.currentDirection) {
      case 'left':
        this.sprite.body.setVelocityX(-this.moveSpeed);
        break;
      case 'right':
        this.sprite.body.setVelocityX(this.moveSpeed);
        break;
      case 'up':
        this.sprite.body.setVelocityY(-this.moveSpeed);
        break;
      case 'down':
        this.sprite.body.setVelocityY(this.moveSpeed);
        break;
    }
    
    if (!this.stuckCheckTimer) {
      this.stuckCheckTimer = this.scene.time.addEvent({
        delay: 500,
        callback: () => {
          const distMoved = Phaser.Math.Distance.Between(
            previousPosition.x, previousPosition.y,
            this.sprite.x, this.sprite.y
          );
          if (distMoved < 5 && this.currentDirection) {
            // The NPC is stuck! We need to choose a new direction
            this.chooseNewDirection();
          }
        },
        callbackScope: this,
        loop: false
      });
    }
    
    // Check if we're moving too far from spawn point
    const distanceFromSpawn = Phaser.Math.Distance.Between(
      this.sprite.x, this.sprite.y,
      this.spawnPoint.x, this.spawnPoint.y
    );
    
    if (distanceFromSpawn > this.roamRadius) {
      // Turn around and head back toward spawn point
      this.sprite.body.setVelocity(0);
      
      const dx = this.spawnPoint.x - this.sprite.x;
      const dy = this.spawnPoint.y - this.sprite.y;
      
      if (Math.abs(dx) > Math.abs(dy)) {
        this.currentDirection = dx > 0 ? 'right' : 'left';
      } else {
        this.currentDirection = dy > 0 ? 'down' : 'up';
      }
      
      const animKey = `${this.id}-${this.getDirectionFromMovement()}-walk`;
      if (this.scene.anims.exists(animKey)) {
        this.sprite.anims.play(animKey);
      } else {
        this.sprite.setTexture(this.atlas, `${this.framePrefix}-${this.getDirectionFromMovement()}`);
      }
      
      // Add a timer to force direction change if they get stuck
      if (this.movementTimer) {
        this.scene.time.removeEvent(this.movementTimer);
      }
      
      this.movementTimer = this.scene.time.delayedCall(1500, () => {
        this.chooseNewDirection();
      });
    }
  }
  
  update(player, isInDialogue) {
    // If in dialogue with the player, stop moving and face them
    if (isInDialogue && this.isPlayerNearby(player)) {
      this.sprite.body.setVelocity(0);
      this.facePlayer(player);
      this.sprite.anims.stop();
      
      // Pause roaming while in dialogue
      if (this.movementTimer) {
        this.scene.time.removeEvent(this.movementTimer);
        this.movementTimer = null;
      }
    } 
    // If player is nearby but not in dialogue, face them but don't move
    else if (this.isPlayerNearby(player)) {
      this.sprite.body.setVelocity(0);
      this.facePlayer(player);
      this.sprite.anims.stop();
      
      // Pause roaming when player is nearby
      if (this.movementTimer) {
        this.scene.time.removeEvent(this.movementTimer);
        this.movementTimer = null;
      }
    } 
    else if (this.isRoaming) {
      if (!this.movementTimer) {
        this.startRoaming();
      }
      
      this.moveInCurrentDirection();
    } else {
      this.sprite.body.setVelocity(0);
    }
    
    // Update name label position
    if (this.nameLabel) {
      this.nameLabel.x = this.sprite.x;
      this.nameLabel.y = this.sprite.y - 40;
    }
  }

  get position() {
    return {
      x: this.sprite.x,
      y: this.sprite.y
    };
  }
  
  get body() {
    return this.sprite;
  }

  createNameLabel() {
    this.nameLabel = this.scene.add.text(0, 0, this.name, {
      font: "14px Arial",
      fill: "#ffffff",
      backgroundColor: "#000000",
      padding: { x: 4, y: 2 },
      align: "center"
    });
    this.nameLabel.setOrigin(0.5, 1);
    this.nameLabel.setDepth(20);
    this.updateNameLabelPosition();
  }

  updateNameLabelPosition() {
    if (this.nameLabel && this.sprite) {
      this.nameLabel.setPosition(
        this.sprite.x,
        this.sprite.y - this.sprite.height/2 - 10
      );
    }
  }

  destroy() {
    if (this.movementTimer) {
      this.scene.time.removeEvent(this.movementTimer);
    }
    if (this.stuckCheckTimer) {
      this.scene.time.removeEvent(this.stuckCheckTimer);
    }
    
    this.nameLabel.destroy();
    this.sprite.destroy();
  }
}

export default Character; 
