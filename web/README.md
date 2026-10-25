# Web app

A React app (built with Vite) where you upload one JPG or PNG image and see if it looks AI-generated. It calls the backend described in [../docs/api-contract.md](../docs/api-contract.md).

## Running it

You need Node.js. From this folder, in PowerShell:

```powershell
npm install
npm run dev
```

The app is at http://localhost:5173. The backend must be running too (see the main README), by default at http://localhost:8000.

To use another backend address, copy `.env.example` to `.env` and change `VITE_API_URL`. The backend must allow the web app's address in its `CORS_ORIGINS` setting. `http://localhost:5173` is allowed by default.

`npm run build` makes the files for deployment in `dist/`.

## Files

```
web/
├── index.html                  the page React is put into
├── vite.config.js              Vite settings (dev server on port 5173)
├── .env.example                the backend address
└── src/
    ├── main.jsx                starts React
    ├── App.jsx                 holds the state: chosen file, loading, result, error
    ├── api.js                  the only file that talks to the backend
    ├── styles.css
    └── components/
        ├── UploadForm.jsx      file picker, preview, Analyze button
        └── ResultCard.jsx      shows the answer
```

## About the result

The backend returns `fake_crop_ratio`, the share of image sections that voted fake. It is not a probability, so the app shows "x of y sections" and never a percentage. The model is also weak on compressed images (JPEG photos, downloaded images), so the app shows a warning under every result.
