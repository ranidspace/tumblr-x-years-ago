#!/usr/bin/env python

import json
from pathlib import Path
from urllib.parse import urlparse

import pytumblr2
from requests_oauthlib import OAuth1Session


def load_config() -> dict:
    """Read config.json from the current directory, creating it if it doesn't
    exist and validate input.
    """
    # Create file if it doesnt exist
    config_path = Path(__file__).with_name("config.json")
    try:
        with config_path.open() as fp:
            config = json.load(fp)

    except (OSError, ValueError):
        print("Invalid or missing config.json, creating one.")
        config = {
            "consumer_key": "",
            "consumer_secret": "",
            "oauth_token": "",
            "oauth_token_secret": "",
            "years_ago": 0,
            "blog": "",
        }

    # Check if blog name is fine
    if len(config["blog"].strip()) == 0:
        blog_name = ""
        while len(blog_name) == 0:
            blog_name = input("Blog name to post to: ").strip()
        config["blog"] = blog_name

    # Check if years ago is valid
    if not isinstance(config["years_ago"], int) and config["years_ago"] < 1:
        years = 0
        while years < 1:
            check = input("How many years to queue posts ahead: ")
            if check.isdigit():
                years = int(check)
            else:
                print("Must be an integer above 0")
                years = 0

    # Check for Tumblr Application consumer credentials
    if not (config["consumer_key"] and config["consumer_secret"]):
        config["consumer_key"] = input(
            "Input Tumblr application consumer key: "
        ).strip()
        config["consumer_secret"] = input(
            "Input Tumblr application secret key: "
        ).strip()

    # Check for OAuth credentials
    if not (config["oauth_token"] and config["oauth_token_secret"]):
        config["oauth_token"], config["oauth_token_secret"] = get_oauth(
            config["consumer_key"],
            config["consumer_secret"],
        )

    # TODO: Only write file if changed
    # Write any changed config to the file
    with config_path.open("w") as fp:
        json.dump(config, fp, indent=4)
    # Load it again for consistency.
    with config_path.open() as fp:
        return json.load(fp)


# CRED: Taken almost directly from tumblr/pytumblr/interactive_console.py
def get_oauth(consumer_key, consumer_secret):
    """Return the consumer and oauth tokens with three-legged OAuth process."""
    request_token_url = "https://www.tumblr.com/oauth/request_token"
    authorize_url = "https://www.tumblr.com/oauth/authorize"
    access_token_url = "https://www.tumblr.com/oauth/access_token"

    # STEP 1: Obtain request token
    oauth_session = OAuth1Session(consumer_key, client_secret=consumer_secret)
    fetch_response = oauth_session.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")

    # STEP 2: Authorize URL + Response
    full_authorize_url = oauth_session.authorization_url(authorize_url)

    # Redirect to authentication page
    print(f"\nPlease go here and authorize:\n{full_authorize_url}")
    redirect_response = input("Allow then paste the full redirect URL here:\n").strip()

    # Retrieve oauth verifier
    oauth_response = oauth_session.parse_authorization_response(redirect_response)

    verifier = oauth_response.get("oauth_verifier")

    # STEP 3: Request final access token
    oauth_session = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth_session.fetch_access_token(access_token_url)

    return oauth_tokens.get("oauth_token"), oauth_tokens.get("oauth_token_secret")


def get_client(config):
    return pytumblr2.TumblrRestClient(
        config["consumer_key"],
        config["consumer_secret"],
        config["oauth_token"],
        config["oauth_token_secret"],
    )


def parse_tags() -> str:
    while True:
        tags = input("Tags (comma separated): ")
        if not tags:
            return ""

        taglist = tags.split(",")

        for i in range(len(taglist)):
            tag = taglist[i].strip()
            if len(tag) > 140:
                temp = tag[:140] + "\033[1;41m" + tag[140:] + "\033[1;49m"
                print(f"Tag {temp} too long, must be 140 characters")
                break
            if len(tag) > 0:
                taglist[i] = tag
        else:
            return taglist


@pytumblr2.validate_blogname
def queue_ahead(blogname, parent_blog_uuid, reblog_key, years):
    url = f"/v2/blog/{blogname}/posts"


def main() -> int:
    config = load_config()
    client = get_client(config)

    years_ago = config["years_ago"]
    blog = config["blog"]

    print(f"Queueing a post {years_ago} years later to {blog}.tumblr.com")

    url = input("Input post URL: ")
    url = urlparse(url)

    # Get body text if needed
    body = input(r"Input post text (\n to start a new block): ").split(r"\n")
    content: list[dict] = []
    if body:
        for text in body:
            parsed = urlparse(text)
            if parsed.scheme and parsed.netloc and len(text.split()) == 1:
                content.extend(
                    [
                        {"type": "link", "url": text.strip()},
                    ]
                )
            else:
                content.extend(
                    [
                        {"type": "text", "text": text.strip()},
                    ]
                )
    tags = parse_tags()

    path = url.path.split("/")
    post_id = int(path[2])

    username = url.netloc.split(".")[0] if path[1] == "post" else path[1]

    post = client.get_single_post(username, post_id)

    date = post["date"]
    year = int(date[0:4])
    date = str(year + years_ago) + date[4:]

    reblog_name = post["blog"]["name"]
    reblog_uuid = post["blog"]["uuid"]

    response = client.reblog_post(
        blog,
        reblog_name,
        post_id,
        reblog_uuid,
        post["reblog_key"],
        publish_on=date,
        state="queue",
        content=content,
        tags=tags,
    )
    print(response["display_text"])


if __name__ == "__main__":
    main()
