# Guess The Song

Experience the magic of trivia with this innovative game! Crafted in real-time, this game adapts, matching each user's unique Spotify taste profile. Whether you're hosting a party or simply jamming out solo, this platform ensures the perfect soundtrack. With support for multiple users and the ability to select songs based on favorite artists, it's the ultimate tool for musical enjoyment and the accompanying dopamine rush. Ready to elevate your music experience? Dive in and discover the future of personalized trivia!

## How the app works:
1) You are prompted for your Spotify, developer credentials, with detailed instructions on how to get them, including the link to a video
2) The credentials you provide are validated and stored locally
3) Then you can choose to generate songs by artist or based on your and your friends' Spotify taste profiles(requires login)
4) If you choose to select by artist a window prompts you to select artists by querying Spotify
5) If you choose to select by Spotify profile a window asks you how many users with a Spotify account would like to log in, and lets them log in one by one
6) Your songs and their details are fetched by SpotifyAPI and added to the pool of songs, in case of selection by artist all the tracks that satisfy a certain popularity threshold are added, in case of selection by Spotify profile the users' top tracks and a mix of tracks recommended to them are added
7) Now you can enjoy the game, in the background the game swaps these song names for YouTube links and plays them to you

## Known Errors :
1) When selecting by artist, the artist's more popular songs may be of a different language than what you would expect. This frequently happens to artists of regional songs.
2) When selecting by artist, an artist's songs may dominate another artist's.
3) Max Retries Exceeded, this happens when you overuse the app. If the app doesn't work or crashes with this exception restart it after 1 minute or change the app credentials

These errors are being worked on and will be resolved. Feel free to contribute



## Disclaimer:    
**This App Exists for educational purposes, is not meant for commercial use or copyright infringement, use at your risk**
