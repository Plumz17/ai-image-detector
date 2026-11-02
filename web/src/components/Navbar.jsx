
export default function Navbar({ active }) {
  return (
    <header className="site-nav">
      <a className="brand-mark" href="/" aria-label="UGM AI Image Detector home">
        <img src="/ugm-logo.png" alt="Universitas Gadjah Mada Logo" />
      </a>

      <nav>
        <a className={active === "home" ? "active" : ""} href="/">
          Home
        </a>

        <a className={active === "about" ? "active" : ""} href="/about">
          About It
        </a>
      </nav>

      <span className="nav-spacer" />
    </header>
  );
}
