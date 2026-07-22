# Chat Deck

The idea behind this plugin is to display and select Twitch chat messages on
a Stream Deck. Why would you want to do this? Well in my case it's so that I
can send the user name and contents of a message off to my stream bot for
display on-screen, so that people watching VODs have context for the message
I'm responding to.

## Compatibility

I have both a Stream Deck v2 and a Stream Deck Plus to test on, so I've been
testing primarily with key and dial controls. For the time being dials are the
primary focus, since that's how I want to interface with it. Currently dials
allow you to move forward and backward through the last *N* messages received
while keys only allow you to move backward. Ultimately I would like to allow
for multiple keys, one for sending the message to the bot and two for navigating,
but I have to work out how to integrate that without overcomplicating what I
already have.

## Usage

### For Dials
Rotating the dial will cycle through messages, clicking the dial down will
send the message to the configured URL.

### For Keys
A short press will move backwards through messages, a long press will send the
message to the configured URL.

# Setup

In order for this plugin to work, you must setup an app integration in your
Twitch dev console. You can do this by following these instructions:

1. Go to [your twitch dev console](https://dev.twitch.tv/console)
    - You may have to log in
2. Click the "Register Your Application" button
3. Name your application
    - This must be unique amongst all applications regiestered by all Twitch
    users
4. Set the "OAuth Redirect URL" to http://localhost:17563
5. Set the "Category" to "Application Integration"
6. Set the "Client Type" to "Confidential"
7. Click "Create"
8. Copy and paste the "Cient ID" and "Client Secret" into their respective
fields in this plugin's global settings page

# Contributing

If you wish to contribute to this project, **PLEASE** do so from the [Codeberg](https://codeberg.org/LanaTheRaven/ChatDeck)
page/repository, not GitHub. Codeberg is the main platform, the GitHub exists
only for eventual inclusion in the StreamController store, is intended to be a
read-only mirror, and will be deleted the instant StreamController and its store
supports other forges. This holds true for all contributions -- whether they be
code, bug reports, or anything else you can think of. Thank you!

# Final Word

Is this messy? Yes.

Does it work? Yes. (To the best of my knowledge)

Is it perfect? Hell no!

However given that I started this project in June 2026, after 15+ years of 
**NOT** doing serious coding and after literally one day of learning Python
*specifically so I could make this* -- I think I did okay. If you want to help
make it better, please by all means submit feedback or code! But only human
generated please, so-called "AI" bullshit isn't allowed!
