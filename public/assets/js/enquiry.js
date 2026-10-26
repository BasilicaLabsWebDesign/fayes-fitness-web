// Enquiry form. For now it opens the visitor's email app with a message to Faye already
// written; when the site sends its own email (phase 5) it will post to /api/enquiry instead.

const TO = "faye@fayesintentionaltraining.com";
const form = document.getElementById("enquiry");

if (form) {
  const status = form.querySelector(".form-status");

  // ?topic=academy (etc.) on the link that brought someone here picks the topic for them
  const topic = new URLSearchParams(location.search).get("topic");
  if (topic && [...form.topic.options].some((o) => o.value === topic)) form.topic.value = topic;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    let firstBad = null;
    for (const el of form.querySelectorAll("[required]")) {
      const ok = el.value.trim() !== "" && el.checkValidity();
      el.setAttribute("aria-invalid", String(!ok));
      if (!ok && !firstBad) firstBad = el;
    }
    if (firstBad) {
      status.textContent = "Just a couple of details missing — please check the highlighted fields.";
      firstBad.focus();
      return;
    }

    const d = new FormData(form);
    const about = form.topic.selectedOptions[0].text;
    const lines = [
      `Name: ${d.get("name")}`,
      `Email: ${d.get("email")}`,
      d.get("phone") ? `Phone: ${d.get("phone")}` : "",
      d.get("organisation") ? `Organisation: ${d.get("organisation")}` : "",
      d.get("date") ? `Date: ${d.get("date")}` : "",
      `About: ${about}`,
      "",
      d.get("message"),
    ].filter((line, i) => line !== "" || i === 6);

    const subject = `Enquiry: ${about} — ${d.get("name")}`;
    const link = document.createElement("a");
    link.href = `mailto:${TO}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
    link.click();
    status.textContent = "Your email app should now open with everything filled in — just press send.";
  });

  form.addEventListener("input", (e) => {
    if (e.target.getAttribute("aria-invalid") === "true" && e.target.checkValidity() && e.target.value.trim()) {
      e.target.setAttribute("aria-invalid", "false");
    }
  });
}
