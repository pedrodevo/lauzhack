# lauzhack
Repository for Lauzhack hackathon.



## Installation

```bash
# 1) create and activate virtual environment
# -- EITHER with conda
conda create -n apis_env python=3.11
conda activate apis
# -- OR with venv
python3.11 -m venv apis_env
source apis_env/bin/activate

# 2) install dependencies
(apis_env) pip install -r requirements.txt
```

## Usage

Our bot is deployed on Telegram. You can find it by searching for `@lauzbert_bot` on Telegram. It has a few useful commands:

- `/start`: start the bot
- `/help`: get help
- `/about`: get information about the bot
- `/testme`: provide a set of test questions about the last uploaded document
- `/related`: `: suggest related study topics # TODO