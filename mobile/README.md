# Mobile app (Android, Expo)

The app calls the shared backend described in [../docs/api-contract.md](../docs/api-contract.md). All network code is in `src/api.ts`: UI code should only use `health()` and `predict(uri, mimeType?, sizeBytes?)`, which throw `ApiError` (`status` 0 = server unreachable, `detail` = the underlying error text) with a `message` to show.

## Run on a phone (Expo Go)
Needs Node.js, and the Expo Go app from the Play Store. The phone and the PC must be on the same Wi-Fi.
```
npm install
cp .env.example .env     # set EXPO_PUBLIC_API_URL to the hosted backend (ask the team); never commit .env
npx expo start           # scan the QR code with Expo Go
```
Set `EXPO_PUBLIC_API_MOCK=1` in `.env` to work without a server. To check the connection on a real phone, make `App.tsx` contain `export { default } from './dev/ApiTestScreen';` (optional debug screen, buttons for internet, server and photo upload).

Notes:
- The project is on **Expo SDK 57** because the Expo Go in the stores supports the newest SDK only after some delay (SDK 58 failed with "requires a newer version of Expo Go"). Upgrade only when Expo Go supports it.
- Expo's `fetch` only uploads real file objects, so `api.ts` sends `new File(uri)` from `expo-file-system`. Do not use the old `{ uri, name, type }` form: it fails with "Unsupported FormData Part".
- Image picker: use `quality: 1` and `allowsEditing: false` so the original bytes are uploaded (the model reads pixel texture). For an APK build, add the `expo-image-picker` plugin to `app.json` (see the Expo docs).
- If the PC is on a phone's hotspot, Expo Go on that same phone may be unable to reach the PC; use a second device or a normal Wi-Fi.

## Android build (installable APK link)
Set `EXPO_PUBLIC_API_URL` as an EAS environment variable, then:
```
npx eas-cli@latest build -p android --profile preview
```
Do not show `fake_crop_ratio` to users as "% chance": it is a vote share.
