import { Scene } from 'phaser';

export class Preloader extends Scene
{
    constructor ()
    {
        super('Preloader');
    }

    preload ()
    {
        this.load.setPath('assets');

        // General assets
        this.load.image('background', 'm_10vscr7.jpg');
        this.load.image('soccerfield', 'soccerfield.jpg');



        // Character assets
        this.load.atlas("sophia", "characters/sophia/atlas.png", "characters/sophia/atlas.json");
        this.load.atlas("messi", "characters/leomessi/atlas.png", "characters/leomessi/atlas.json"); 
        this.load.atlas("kaka", "characters/kaka/atlas.png", "characters/kaka/atlas.json"); 
        this.load.atlas("ronaldonazario", "characters/ronaldonazario/atlas.png", "characters/ronaldonazario/atlas.json"); 
        this.load.atlas("maradona", "characters/maradona/atlas.png", "characters/maradona/atlas.json"); 
        this.load.atlas("ronaldo", "characters/cristianoronaldo/atlas.png", "characters/cristianoronaldo/atlas.json"); 
        this.load.atlas("sergioramos", "characters/sergioramos/atlas.png", "characters/sergioramos/atlas.json"); 
        this.load.atlas("pepguardiola", "characters/pepguardiola/atlas.png", "characters/pepguardiola/atlas.json"); 
        this.load.atlas("alexferguson", "characters/alexferguson/atlas.png", "characters/alexferguson/atlas.json"); 
        this.load.atlas("ancelotti", "characters/ancelotti/atlas.png", "characters/ancelotti/atlas.json"); 
        this.load.atlas("neymar", "characters/neymar/atlas.png", "characters/neymar/atlas.json"); 
        this.load.atlas("jurgenklopp", "characters/jurgenklopp/atlas.png", "characters/jurgenklopp/atlas.json"); 
    }

    create ()
    {
        this.scene.start('MainMenu');
    }
}
