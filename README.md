# PySnake

# Description

This project is a snake game inspired by Google's snake game : https://www.google.com/fbx?fbx=snake_arcade.
It is designed to be both scalable and high performance.

## Getting Started

# Prerequisites
- Python: version 3.13 recommended and latest pip
- IDE: Pycharm ou alternative that support python
- Virtualization: virtual environment (.venv)


**upgrade pip for Linux and MacOS**
``` bash
python -m ensurepip --upgrade
```

**upgrade pip for Windows**
``` bash
py -m ensurepip --upgrade
```

# Librairies
- Pygame: 2.6.1

# Tool used
- IDE: Pycharm 2025.2.1.1


## Deployment

1.
**clone the repository**
``` bash
git clone https://github.com/MouldiAchouri/PySnakeTPI.git
cd PySnake
```

2.
**Creation and activation of the virtual environment**
```bash
python -m venv .venv
```
# Windows
```bash
.\.venv\Scripts\activate
```

# Linux/Mac
```bash
source .venv/bin/activate
```

3.
**Installation of dependencies**
```bash
pip install -r requirements.txt
```
4.
**Launch the game**
```bash
python main.py
```

# Directory structure

```text
├── config/
│   └── constants.py       
├── data/
│   └── scores.json        
├── game/
│   ├── apple.py         
│   ├── game.py          
│   ├── menu.py            
│   └── snake.py           
├── view/
│   ├── render.py         
│   ├── state_render.py   
│   └── window_manager.py  
├── score_manager.py      
├── main.py               
├── .env                  
└── requirements.txt
```

# Collaboration

Use issues for discussions and pull requests to submit changes.

# How to commit
This project follows this convention : **Conventional Commits**
URL: https://www.conventionalcommits.org/en/v1.0.0/

# How to use your workflow
Each new feature must be developed on a branch named feature/name_of_the_feature
Branches are merged into develop after validation

# Contact 

If you have any questions, please contact me by:
- Email : mouldi.achouri@eduvaud.ch
- Issue : sur le dépôt Github