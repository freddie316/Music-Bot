# PyTunes
A Discord music bot for playing youtube audio

### Commands - Prefix: !
- join - joins your current voice channel.
- leave - exits the current voice channel.
- play [query] - will attempt to join your voice channel and will play the audio from the query.
    - Query can either be a youtube URL or a video title. Video titles should be in quotes, PyTunes will return the top three results from the search.
    - Examples:
        - URL: !play https://www.youtube.com/watch?v=dQw4w9WgXcQ
        - Title: !play "Never gonna give you up"
- stop - will stop playing whatever is currently playing.
- repeat - will repeat the current song until disabled.
- help - displays this information about the commands.
- shutdown - bot owner only, closes the bots connection to discord.
- ping - pong!

### Other Features
- Will queue additional song requests.
- PyTunes will disconnect from voice after 5 minutes of inactivity.
