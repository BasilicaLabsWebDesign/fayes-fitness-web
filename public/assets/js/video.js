// Click-to-play YouTube. Each video shows our own poster until someone taps play,
// so nothing is requested from YouTube before a visitor chooses to watch.

for (const btn of document.querySelectorAll("[data-youtube]")) {
  btn.addEventListener("click", () => {
    const frame = document.createElement("iframe");
    frame.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(btn.dataset.youtube)}?autoplay=1&rel=0&playsinline=1`;
    frame.title = btn.dataset.title || "Video";
    frame.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen";
    frame.allowFullscreen = true;
    btn.replaceWith(frame);
    frame.focus();
  });
}
