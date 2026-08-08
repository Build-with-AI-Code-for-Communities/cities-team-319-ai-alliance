# CoralAI Mobile (Android)

A native Android build of CoralAI, generated separately from the web app. It talks to the
same backend as the website (`https://cities-team-319-ai-alliance.onrender.com/api`) — see
[docs/api-design.md](../docs/api-design.md) for the exact request/response shape of every
endpoint.


## Installing on an Android phone

1. Download `coral-ai.apk` onto the phone (via the repo's GitHub page, a direct release
   link, or transferred over USB/cloud storage).
2. Android blocks installs from outside the Play Store by default. When you tap the file,
   Android will prompt to allow installs from that source (Files app / Chrome / whichever
   app opened it) — tap **Settings** → enable **Allow from this source**.
3. Tap the APK again → **Install**.
4. On first launch, grant the permissions it asks for (**Camera**, **Photos/Storage**,
   **Location**) — the upload flow needs at least one of Camera/Photos, and Location is
   used the same way the web app's browser-geolocation fallback is: only when a photo has
   no GPS EXIF data.


      30-50 seconds rather than fail. Make sure the app shows a loading state instead of
      looking frozen or erroring out.
- [ ] Test on real mobile data (not just wifi), since judges may demo it that way.



