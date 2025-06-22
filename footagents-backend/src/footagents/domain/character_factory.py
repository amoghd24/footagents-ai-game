from .models import FootballLegend
from typing import List


FOOTBALL_LEGENDS = {
    "messi": "Lionel Messi",
    "ronaldo": "Cristiano Ronaldo", 
    "maradona": "Diego Maradona",
    "pele": "Pelé",
    "kaka": "Kaká",
    "ronaldinho": "Ronaldinho",
}

LEGEND_POSITIONS = {
    "messi": "Right Winger / False 9",
    "ronaldo": "Left Winger / Striker",
    "maradona": "Attacking Midfielder / Second Striker",
    "pele": "Attacking Midfielder / Forward",
    "kaka": "Attacking Midfielder",
    "ronaldinho": "Attacking Midfielder / Left Winger",
}

LEGEND_ERAS = {
    "messi": "2000s-2020s",
    "ronaldo": "2000s-2020s", 
    "maradona": "1980s-1990s",
    "pele": "1960s-1970s",
    "kaka": "2000s-2010s",
    "ronaldinho": "2000s-2010s",
}

LEGEND_PERSPECTIVES = {
    "messi": """Messi is humble and team-focused. He believes football is about creativity, 
    technique, and making your teammates better. He emphasizes the importance of hard work, 
    patience, and enjoying the beautiful game.""",
    
    "ronaldo": """Ronaldo is confident and motivational. He believes in self-improvement, 
    dedication, and never giving up. He focuses on physical preparation, mental strength, 
    and always striving to be the best version of yourself.""",
    
    "maradona": """Maradona is passionate and emotional. He believes football is art, 
    creativity, and expressing yourself. He talks about playing with heart, the magic 
    of street football, and connecting with the people.""",
}

LEGEND_STYLES = {
    "messi": """Messi speaks softly and thoughtfully. He's modest about his achievements 
    and focuses on the team. His responses are calm, insightful, and often mention 
    teammates and coaches who helped him.""",
    
    "ronaldo": """Ronaldo is energetic and confident. He speaks with passion about 
    hard work and dedication. He's motivational and direct, often sharing training 
    tips and mental preparation advice.""",
    
    "maradona": """Maradona is expressive and passionate. He speaks with emotion about 
    the beautiful game, uses colorful language, and tells stories about his playing days. 
    He's charismatic and connects football to life.""",
}


class FootballLegendFactory:
    @staticmethod
    def get_legend(legend_id: str) -> FootballLegend:
        legend_id = legend_id.lower()
        
        if legend_id not in FOOTBALL_LEGENDS:
            raise ValueError(f"Legend {legend_id} not found")
            
        return FootballLegend(
            id=legend_id,
            name=FOOTBALL_LEGENDS[legend_id],
            position=LEGEND_POSITIONS[legend_id],
            era=LEGEND_ERAS[legend_id],
            perspective=LEGEND_PERSPECTIVES.get(legend_id, ""),
            style=LEGEND_STYLES.get(legend_id, ""),
            career_highlights=""
        )
    
    @staticmethod
    def get_available_legends() -> List[str]:
        return list(FOOTBALL_LEGENDS.keys()) 