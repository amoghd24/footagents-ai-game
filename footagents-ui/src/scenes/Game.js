import { Scene } from 'phaser';
import Character from '../classes/Character';
import DialogueBox from '../classes/DialogueBox';
import DialogueManager from '../classes/DialogueManager';

export class Game extends Scene
{
    constructor ()
    {
        super('Game');
        this.controls = null;
        this.player = null;
        this.cursors = null;
        this.dialogueBox = null;
        this.spaceKey = null;
        this.activePlayer = null;
        this.dialogueManager = null;
        this.players = [];
        this.labelsVisible = true;
    }

    create ()
    {
        // Add soccer field background
        this.soccerField = this.add.image(0, 0, 'soccerfield').setOrigin(0, 0);
        
        // Scale to fit screen while maintaining aspect ratio
        const scaleX = this.cameras.main.width / this.soccerField.width;
        const scaleY = this.cameras.main.height / this.soccerField.height;
        const scale = Math.max(scaleX, scaleY);
        this.soccerField.setScale(scale);
        
        // Center the background
        this.soccerField.x = (this.cameras.main.width - this.soccerField.displayWidth) / 2;
        this.soccerField.y = (this.cameras.main.height - this.soccerField.displayHeight) / 2;
        
        let screenPadding = 20;
        let maxDialogueHeight = 200;

        this.createPlayers();

        this.setupPlayer();
        const camera = this.setupCamera();

        this.setupControls(camera);

        this.setupDialogueSystem();

        this.dialogueBox = new DialogueBox(this);
        this.dialogueText = this.add
            .text(60, this.game.config.height - maxDialogueHeight - screenPadding + screenPadding, '', {
            font: "18px monospace",
            fill: "#ffffff",
            padding: { x: 20, y: 10 },
            wordWrap: { width: 680 },
            lineSpacing: 6,
            maxLines: 5
            })
            .setScrollFactor(0)
            .setDepth(30)
            .setVisible(false);

        this.spaceKey = this.input.keyboard.addKey('SPACE');
        
        // Initialize the dialogue manager
        this.dialogueManager = new DialogueManager(this);
        this.dialogueManager.initialize(this.dialogueBox);
    }

    createPlayers() {
        const playerConfigs = [
            { id: "leomessi", name: "Leo Messi", defaultDirection: "right", roamRadius: 200, x: 200, y: 150 },
            { id: "ronaldonazario", name: "Ronaldo Nazario", defaultDirection: "right", roamRadius: 180, x: 400, y: 200 },
            { id: "kaka", name: "KAKA", defaultDirection: "front", roamRadius: 150, x: 600, y: 150 },
            { id: "maradona", name: "Maradona", defaultDirection: "front", roamRadius: 160, x: 800, y: 300 },
            { id: "cristianoronaldo", name: "Cristiano Ronaldo", defaultDirection: "front", roamRadius: 170, x: 300, y: 400 },
            { id: "sergioramos", name: "Sergio Ramos", defaultDirection: "front", roamRadius: 180, x: 150, y: 350 },
            { id: "pepguardiola", name: "Pep Guardiola", defaultDirection: "front", roamRadius: 150, x: 550, y: 300 },
            { id: "alexferguson", name: "Alex Ferguson", defaultDirection: "front", roamRadius: 160, x: 350, y: 250 },
            { id: "ancelotti", name: "Ancelotti", defaultDirection: "front", roamRadius: 170, x: 750, y: 200 },
            { 
                id: "neymar", 
                name: "Neymar", 
                defaultDirection: "front", 
                roamRadius: 120,
                x: 500, y: 500,
                defaultMessage: "Hey there! I'm Neymar Jr! Want to know some football tricks? I'm always ready to talk about the beautiful game!" 
            },
            { 
                id: "jurgenklopp", 
                name: "Jurgen Klopp", 
                defaultDirection: "front",
                roamRadius: 120,
                x: 650, y: 500,
                defaultMessage: "Hello! I'm Jurgen Klopp. Football is about passion, teamwork, and never giving up. Let's talk tactics!" 
            }
        ];

        this.players = [];
        
        playerConfigs.forEach(config => {
            const spawnPoint = { x: config.x, y: config.y };
            
            this[config.id] = new Character(this, {
                id: config.id,
                name: config.name,
                spawnPoint: spawnPoint,
                atlas: config.id,
                defaultDirection: config.defaultDirection,
                worldLayer: null, // No collision layer for soccer field
                defaultMessage: config.defaultMessage,
                roamRadius: config.roamRadius,
                moveSpeed: config.moveSpeed || 40,
                pauseChance: config.pauseChance || 0.2,
                directionChangeChance: config.directionChangeChance || 0.3,
                handleCollisions: true
            });
            
            this.players.push(this[config.id]);
        });

        // Make all player labels visible initially
        this.togglePlayerLabels(true);

        // Add collisions between players
        for (let i = 0; i < this.players.length; i++) {
            for (let j = i + 1; j < this.players.length; j++) {
                this.physics.add.collider(
                    this.players[i].sprite, 
                    this.players[j].sprite
                );
            }
        }
    }

    checkPlayerInteraction() {
        let nearbyPlayer = null;

        for (const player of this.players) {
            if (player.isPlayerNearby(this.player)) {
                nearbyPlayer = player;
                break;
            }
        }
        
        if (nearbyPlayer) {
            if (Phaser.Input.Keyboard.JustDown(this.spaceKey)) {
                if (!this.dialogueBox.isVisible()) {
                    this.dialogueManager.startDialogue(nearbyPlayer);
                } else if (!this.dialogueManager.isTyping) {
                    this.dialogueManager.continueDialogue();
                }
            }
            
            if (this.dialogueBox.isVisible()) {
                nearbyPlayer.facePlayer(this.player);
            }
        } else if (this.dialogueBox.isVisible()) {
            this.dialogueManager.closeDialogue();
        }
    }



    setupPlayer() {
        // Center player spawn point on soccer field
        const spawnPoint = { x: 512, y: 350 }; // Center of typical soccer field
        this.player = this.physics.add.sprite(spawnPoint.x, spawnPoint.y, "sophia", "sophia-front")
            .setSize(30, 40)
            .setOffset(0, 6);

        // Add collisions between player and players
        this.players.forEach(player => {
            this.physics.add.collider(this.player, player.sprite);
        });

        this.createPlayerAnimations();

        // Set world bounds for physics - use soccer field dimensions
        this.physics.world.setBounds(0, 0, this.soccerField.displayWidth, this.soccerField.displayHeight);
        this.physics.world.setBoundsCollision(true, true, true, true);
    }

    createPlayerAnimations() {
        const anims = this.anims;
        const animConfig = [
            { key: "sophia-left-walk", prefix: "sophia-left-walk-" },
            { key: "sophia-right-walk", prefix: "sophia-right-walk-" },
            { key: "sophia-front-walk", prefix: "sophia-front-walk-" },
            { key: "sophia-back-walk", prefix: "sophia-back-walk-" }
        ];
        
        animConfig.forEach(config => {
            anims.create({
                key: config.key,
                frames: anims.generateFrameNames("sophia", { prefix: config.prefix, start: 0, end: 8, zeroPad: 4 }),
                frameRate: 10,
                repeat: -1,
            });
        });
    }

    setupCamera() {
        const camera = this.cameras.main;
        camera.startFollow(this.player);
        camera.setBounds(0, 0, this.soccerField.displayWidth, this.soccerField.displayHeight);
        return camera;
    }

    setupControls(camera) {
        this.cursors = this.input.keyboard.createCursorKeys();
        this.controls = new Phaser.Cameras.Controls.FixedKeyControl({
            camera: camera,
            left: this.cursors.left,
            right: this.cursors.right,
            up: this.cursors.up,
            down: this.cursors.down,
            speed: 0.5,
        });
        
        this.labelsVisible = true;
        
        // Add ESC key for pause menu
        this.input.keyboard.on('keydown-ESC', () => {
            if (!this.dialogueBox.isVisible()) {
                this.scene.pause();
                this.scene.launch('PauseMenu');
            }
        });
    }

    setupDialogueSystem() {
        const screenPadding = 20;
        const maxDialogueHeight = 200;
        
        this.dialogueBox = new DialogueBox(this);
        this.dialogueText = this.add
            .text(60, this.game.config.height - maxDialogueHeight - screenPadding + screenPadding, '', {
                font: "18px monospace",
                fill: "#ffffff",
                padding: { x: 20, y: 10 },
                wordWrap: { width: 680 },
                lineSpacing: 6,
                maxLines: 5
            })
            .setScrollFactor(0)
            .setDepth(30)
            .setVisible(false);

        this.spaceKey = this.input.keyboard.addKey('SPACE');
        
        this.dialogueManager = new DialogueManager(this);
        this.dialogueManager.initialize(this.dialogueBox);
    }

    update(time, delta) {
        const isInDialogue = this.dialogueBox.isVisible();
        
        if (!isInDialogue) {
            this.updatePlayerMovement();
        }
        
        this.checkPlayerInteraction();
        
        this.players.forEach(player => {
            player.update(this.player, isInDialogue);
        });
        
        if (this.controls) {
            this.controls.update(delta);
        }
    }

    updatePlayerMovement() {
        const speed = 175;
        const prevVelocity = this.player.body.velocity.clone();
        this.player.body.setVelocity(0);

        if (this.cursors.left.isDown) {
            this.player.body.setVelocityX(-speed);
        } else if (this.cursors.right.isDown) {
            this.player.body.setVelocityX(speed);
        }

        if (this.cursors.up.isDown) {
            this.player.body.setVelocityY(-speed);
        } else if (this.cursors.down.isDown) {
            this.player.body.setVelocityY(speed);
        }

        this.player.body.velocity.normalize().scale(speed);

        const currentVelocity = this.player.body.velocity.clone();
        const isMoving = Math.abs(currentVelocity.x) > 0 || Math.abs(currentVelocity.y) > 0;
        
        if (this.cursors.left.isDown && isMoving) {
            this.player.anims.play("sophia-left-walk", true);
        } else if (this.cursors.right.isDown && isMoving) {
            this.player.anims.play("sophia-right-walk", true);
        } else if (this.cursors.up.isDown && isMoving) {
            this.player.anims.play("sophia-back-walk", true);
        } else if (this.cursors.down.isDown && isMoving) {
            this.player.anims.play("sophia-front-walk", true);
        } else {
            this.player.anims.stop();
            if (prevVelocity.x < 0) this.player.setTexture("sophia", "sophia-left");
            else if (prevVelocity.x > 0) this.player.setTexture("sophia", "sophia-right");
            else if (prevVelocity.y < 0) this.player.setTexture("sophia", "sophia-back");
            else if (prevVelocity.y > 0) this.player.setTexture("sophia", "sophia-front");
            else {
                // If prevVelocity is zero, maintain current direction
                // Get current texture frame name
                const currentFrame = this.player.frame.name;
                
                // Extract direction from current animation or texture
                let direction = "front"; // Default
                
                // Check if the current frame name contains direction indicators
                if (currentFrame.includes("left")) direction = "left";
                else if (currentFrame.includes("right")) direction = "right";
                else if (currentFrame.includes("back")) direction = "back";
                else if (currentFrame.includes("front")) direction = "front";
                
                // Set the static texture for that direction
                this.player.setTexture("sophia", `sophia-${direction}`);
            }
        }
    }

    togglePlayerLabels(visible) {
        this.players.forEach(player => {
            if (player.nameLabel) {
                player.nameLabel.setVisible(visible);
            }
        });
    }
}
