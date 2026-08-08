# CoralAI Mobile (Android)

A native Android build of CoralAI, generated separately from the web app. It talks to the
same backend as the website (`https://cities-team-319-ai-alliance.onrender.com/api`) — see
[docs/api-design.md](../docs/api-design.md) for the exact request/response shape of every
endpoint.

## Where the APK goes

Put the built file here as:

```
mobile/coral-ai.apk
```

(Overwrite it on each new build — keep the filename stable so the download link doesn't change.)

**Before you push it, check the file size:**

```bash
ls -lh mobile/coral-ai.apk
```

- **Under ~25MB:** fine to commit directly to the repo (instructions below).
- **Over ~25MB:** GitHub's web upload UI will reject it, and committing a large binary
  bloats the repo's history permanently. Use a **GitHub Release** instead — attach the APK
  as a release asset (up to 2GB, doesn't bloat the repo, and gives you a stable download
  link). From a machine with `gh` installed: `gh release create android-v1 mobile/coral-ai.apk --title "CoralAI Android v1"`.
  From the GitHub website: go to the repo → **Releases** → **Draft a new release** →
  attach the file.

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

## Pushing the APK from your phone

You don't need a full git setup to do this — pick whichever is easiest:

**Easiest: GitHub's website, no git required**
1. Open `github.com/Build-with-AI-Code-for-Communities/cities-team-319-ai-alliance` in
   your phone's browser, sign in.
2. Navigate into the `mobile/` folder → **Add file** → **Upload files**.
3. Select `coral-ai.apk` from your phone's storage, write a commit message, commit
   directly to `main`.
4. This only works if the file is under GitHub's web-upload limit (~25MB) — if it's
   bigger, use a Release instead (also doable from the website: **Releases** → **Draft a
   new release** → attach the file, no git needed either).

**If you actually want real `git push` from your phone: install Termux**
1. Install [Termux](https://f-droid.org/packages/com.termux/) (use the F-Droid build, not
   the outdated Play Store one).
2. In Termux: `pkg install git`
3. GitHub no longer accepts your account password for git operations — you need a
   [Personal Access Token](https://github.com/settings/tokens) (classic token, `repo`
   scope) generated from GitHub's website, used as the password when git prompts for one.
4. `git clone https://github.com/Build-with-AI-Code-for-Communities/cities-team-319-ai-alliance.git`
5. Copy the APK into `mobile/` inside that cloned folder (Termux can access phone storage
   after running `termux-setup-storage`), then:
   ```bash
   git add mobile/coral-ai.apk
   git commit -m "Add Android APK build"
   git push
   ```

Either way works fine — the website route is faster if you just need the file in the repo
before a deadline.
