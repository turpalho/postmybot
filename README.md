# About docnot_bot

AI-based German language practice bot.

## INSTALLATION

Copy the repository to your directory with the command:

```
    $ git clone https://github.com/turpalho/lernedeutsch.git
```

## QUICK START

Make a copy of .env.dist and remove .dist:

```
    .env
    .env.dist
```

Create a /voice/ folder in the source/ directory:

```
.
├── source/
│   ├── videos/
│   └── voice/
```

Create new bot in telegram with [botFather](https://t.me/BotFather).
Assign the token to a variable in the .env file and your user id to a vatiable "ADMINS":

```
    BOT_TOKEN=your_bot_token
    ADMINS=1234,your_user_id
```

Receive a token from Yookassa in the payment settings of your bot and paste this token into the .env file:

```
YOOKASSA_TOKEN=test_yookassa_token  # Test
# YOOKASSA_TOKEN=live_yookassa_token  # Live
```

The last step is to get a token from [openai](https://platform.openai.com/api-keys):

```
OPENAI_TOKEN=openai_token
```

Run docker-compose

```
    $ docker-compose build
    $ docker-cimpose up
```
