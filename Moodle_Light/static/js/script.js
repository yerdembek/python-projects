async function renderCourses() {
  const ul = document.querySelector("ul");
  const res = await fetch("/api/courses"); // GET
  if (!res.ok) { ul.innerHTML = <li>Ошибка ${res.status}</li>; return; }
  const courses = await res.json();
  if (!courses.length) { ul.innerHTML = "<li>Курсов пока нет</li>"; return; }
  ul.innerHTML = courses.map(c => <li>${c.title}</li>).join("");
}
renderCourses();

async function loadCourses() {
  const ul = document.getElementById("courses");
  ul.innerHTML = "<li>Загрузка…</li>";
  const res = await fetch("/api/courses");
  if (!res.ok) { ul.innerHTML = <li>Ошибка ${res.status}</li>; return; }
  const courses = await res.json();
  if (!courses.length) { ul.innerHTML = "<li>Курсов пока нет</li>"; return; }
  ul.innerHTML = courses.map(c => <li>[${c.id}] ${c.title}</li>).join("");
}

document.getElementById("addCourse").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const title = fd.get("title").trim();
  if (!title) return;

  const res = await fetch("/api/courses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title })
  });

  if (res.ok) {
    e.target.reset();
    await loadCourses();
  } else {
    const err = await res.json().catch(() => ({}));
    alert("Не удалось добавить: " + (err.error || res.status));
  }
});

loadCourses();