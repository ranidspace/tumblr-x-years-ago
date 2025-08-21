# Tumblr X years ago

This script allows you to enter in a URL of a tumblr post, and will schedule it
to exactly 10 years (or however many years) from when it was posted.

This allows you to create a "10 years ago" blog, so you see posts from a
certain amount of time ago as they were being posted.

## Setup

Clone this repository or just download the python file, optionally create a
venv, then run `pip install PyTumblr2`.

You will need a tumblr application consumer and secret token, you can get this
by visiting [tumblr's application page](https://www.tumblr.com/oauth/apps) and
creating a new one. The "Application Website", "Administrative contact email",
and "Default callback URL" can be anything (I have the last one set to
`http://localhost:3000/__/auth/tumblr`, in case I do something with it), the
"OAuth2 redirect URLs" are not required.

Once it is created, it will show an "OAuth Consumer Key", and a button which
says "Show secret key", paste these in during the setup when it asks.

## Usage

```bash
python tumblryearsago.py
```

No command line arguments. On first run it will ask for a blog name to post to,
how many years after the post was made to schedule it for, and then the
Application tokens from before. Once it asks for a URL, the config has been
written.

When it asks you to paste in the URL after inputting the tokens, likely the
page after pressing "Allow" wont be a real page. Copying the URL from the bar
and pasting it in will still work.

You can add text to the post, to make multiple paragraphs type `\n` in between
each (whitespace padding is removed automatically). A single url in a paragraph
will be automatically converted to a link.

Tags are comma separated, and it will warn you if a tag is above the character
limit, and will automatically remove any padding.

If better control over the post is needed, you can always edit the post in the
queue afterwards.
