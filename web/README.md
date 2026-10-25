# Web app

A small React app (built with Vite). You drag an image onto the box (or click it to choose one), it is sent to the backend straight away, and the page shows the label, the crop numbers, the HTTP status and the raw JSON. Errors from the backend are shown the same way. The backend is described in [../docs/api-contract.md](../docs/api-contract.md).

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
    ├── App.jsx                 the drop zone, the preview and the answer
    ├── api.js                  the only file that talks to the backend
    ├── styles.css
    ├── pages/                  empty for now, for the real UI later
    │   ├── Home.jsx            the upload page
    │   └── About.jsx           the about page
    └── components/             empty for now
        ├── Navbar.jsx          Home and About links
        ├── DropZone.jsx        drag and drop box
        ├── ImagePreview.jsx    the chosen image
        └── ResultCard.jsx      the answer from the backend
```

## About the result

The backend returns `fake_crop_ratio`, the share of image sections that voted fake. It is not a probability, so the page shows it as a number next to the crop count and never as a percentage. The model is also weak on compressed images (JPEG photos, downloaded images).
