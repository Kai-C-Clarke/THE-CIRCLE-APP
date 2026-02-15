# The Cast — Email Service

Background worker that monitors Zoho Mail and replies to emails in character.

## Characters

- henry@askian.net → Henry VIII
- tesla@askian.net → Nikola Tesla
- shakespeare@askian.net → William Shakespeare
- ada@askian.net → Ada Lovelace
- davinci@askian.net → Leonardo da Vinci
- churchill@askian.net → Winston Churchill
- dave@askian.net → Dave Nutley
- chantelle@askian.net → Chantelle Briggs
- jade@askian.net → Jade Rampling-Cross
- tarquin@askian.net → Tarquin Worthington-Smythe
- askian@askian.net → Ian

## Render Setup

Deploy as a **Background Worker** with:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python askian_v4.py`

## Environment Variables

Set these in Render dashboard:

- `ZOHO_EMAIL` — your Zoho account email
- `ZOHO_PASSWORD` — your Zoho app password
- `DEEPSEEK_API_KEY` — your DeepSeek API key
