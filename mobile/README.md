# Mobile app (Android, Expo)

The app calls the shared backend described in [../docs/api-contract.md](../docs/api-contract.md). All network code is in `src/api.ts`: UI code should only use `health()` and `predict(uri, mimeType, sizeBytes?)`, which throw `ApiError` (`status` 0 = server unreachable) with a `message` to show.

## Run
```
npm install
cp .env.example .env     # set EXPO_PUBLIC_API_URL, or EXPO_PUBLIC_API_MOCK=1 to work without a server
npx expo start
```
Image picker: use `quality: 1` and `allowsEditing: false`, so the original bytes are uploaded (the model reads pixel texture).

## Android build (installable APK link)
Set `EXPO_PUBLIC_API_URL` (the HTTPS backend URL) as an EAS environment variable, then:
```
npx eas-cli@latest build -p android --profile preview
```
Do not show `fake_crop_ratio` to users as "% chance": it is a vote share.
