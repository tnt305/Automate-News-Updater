from dataclasses import dataclass


@dataclass
class Paper:
    name: str
    id: str
    upvote: int
    original_keywords: list
    description: str
    
@dataclass
class GithubTrend:
    repo: str
    description: str
    start_gain_today: int