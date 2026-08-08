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

## Testing checklist

Run through the same pipeline the web app uses, since they hit the identical backend:

- [ ] Upload a real coral photo (camera or gallery) — confirms `POST /api/upload` works
      from the app's network layer, not just a browser.
- [ ] Confirm a real classification comes back (not "Unknown") — confirms the app's
      `POST /api/analyze` request body matches the API's expected JSON shape.
- [ ] Try a photo with no GPS EXIF and confirm the app either asks for location permission
      or falls back gracefully — don't let it silently send `null, null` if avoidable.
- [ ] Check the survey shows up on the **Dashboard** at the live web URL — confirms both
      clients are reading from the same database, not separate state.
- [ ] Generate and open a PDF report from the app.
- [ ] Test on a cold backend: wait 15+ minutes without using the app/website, then try an
      upload. Render's free tier spins down when idle — expect the first request to take
      30-50 seconds rather than fail. Make sure the app shows a loading state instead of
      looking frozen or erroring out.
- [ ] Test on real mobile data (not just wifi), since judges may demo it that way.



