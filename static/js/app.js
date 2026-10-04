const state = {
  config: null,
  visibleDate: new Date(),
  selectedDate: null,
  monthSchedule: {},
};

const fmt = new Intl.DateTimeFormat("zh-CN", {
  year: "numeric",
  month: "long",
});

function isoDate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function parseLocalDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

async function getJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`Request failed: ${url}`);
  return response.json();
}

function setVisibleMonth(date) {
  state.visibleDate = new Date(date.getFullYear(), date.getMonth(), 1);
}

async function loadMonth() {
  const y = state.visibleDate.getFullYear();
  const m = state.visibleDate.getMonth() + 1;
  const data = await getJson(`/api/schedule?year=${y}&month=${m}`);
  state.monthSchedule = data.month_days;
  renderCalendar();
}

function renderCalendar() {
  const grid = document.getElementById("calendarGrid");
  grid.innerHTML = "";
  document.getElementById("monthTitle").textContent = fmt.format(state.visibleDate);

  const year = state.visibleDate.getFullYear();
  const month = state.visibleDate.getMonth();
  const first = new Date(year, month, 1);
  const startOffset = (first.getDay() + 6) % 7;
  const start = new Date(year, month, 1 - startOffset);
  const today = isoDate(new Date());

  for (let i = 0; i < 42; i += 1) {
    const current = new Date(start);
    current.setDate(start.getDate() + i);
    const key = isoDate(current);
    const info = state.monthSchedule[key];
    const button = document.createElement("button");
    button.type = "button";
    button.className = "day-cell";
    button.textContent = current.getDate();
    if (current.getMonth() === month) button.classList.add("in-month");
    if (info?.has_workout) button.classList.add("has-workout");
    if (info?.completed) button.classList.add("completed");
    if (key === today) button.classList.add("today");
    if (key === state.selectedDate) button.classList.add("selected");
    button.addEventListener("click", () => selectDate(key));
    grid.appendChild(button);
  }
}

async function selectDate(dayKey) {
  state.selectedDate = dayKey;
  const date = parseLocalDate(dayKey);
  if (
    date.getFullYear() !== state.visibleDate.getFullYear() ||
    date.getMonth() !== state.visibleDate.getMonth()
  ) {
    setVisibleMonth(date);
    await loadMonth();
  } else {
    renderCalendar();
  }
  await loadDay(dayKey);
}

function taskCard(item, done = false) {
  const card = document.createElement("article");
  card.className = `task-card${done ? " done" : ""}`;
  card.dataset.optionId = item.id;
  card.innerHTML = `
    <div class="stage">${item.stage}</div>
    <h3>${item.title}</h3>
    <p>${item.summary}</p>
    <div class="task-actions">
      <button type="button" class="secondary detail">图文指导</button>
      <button type="button" class="${done ? "secondary undo" : "primary finish"}">${done ? "撤销" : "完成"}</button>
    </div>
  `;
  card.querySelector(".detail").addEventListener("click", () => showDetail(item.id));
  const actionButton = card.querySelector(done ? ".undo" : ".finish");
  actionButton.addEventListener("click", () =>
    done ? uncheck(item.id) : checkin(item.id)
  );
  return card;
}

function renderList(targetId, items, done = false) {
  const target = document.getElementById(targetId);
  target.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = done ? "暂无已完成项目" : "没有待完成项目";
    target.appendChild(empty);
    return;
  }
  items.forEach((item) => target.appendChild(taskCard(item, done)));
}

async function loadDay(dayKey) {
  const data = await getJson(`/api/day?date=${dayKey}`);
  document.getElementById("selectedDate").textContent = dayKey;
  document.getElementById("dayTitle").textContent = data.title;
  renderList("pendingList", data.pending, false);
  renderList("completedList", data.completed, true);
  await loadStats();
}

async function checkin(optionId) {
  await getJson("/api/checkin", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date: state.selectedDate, option_id: optionId }),
  });
  await loadDay(state.selectedDate);
  await loadMonth();
}

async function uncheck(optionId) {
  await getJson("/api/uncheck", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date: state.selectedDate, option_id: optionId }),
  });
  await loadDay(state.selectedDate);
  await loadMonth();
}

async function showDetail(optionId) {
  const detail = await getJson(`/api/exercise?id=${optionId}`);
  document.getElementById("detailStage").textContent = detail.stage;
  document.getElementById("detailTitle").textContent = detail.title;
  const media = document.getElementById("detailMedia");
  media.innerHTML = "";
  const images = detail.images?.length ? detail.images : (detail.image ? [{ src: detail.image, alt: detail.title }] : []);
  images.forEach((item) => {
    const img = document.createElement("img");
    img.src = item.src;
    img.alt = item.alt || detail.title;
    media.appendChild(img);
  });

  const actionWrap = document.getElementById("detailActions");
  actionWrap.innerHTML = "";
  detail.actions.forEach((action) => {
    const item = document.createElement("section");
    item.className = "action-detail";
    item.innerHTML = `
      <h3>${action.name}</h3>
      <p class="meta">${action.sets} · ${action.reps} · 组间休息${action.rest}</p>
      <p>${action.guide}</p>
    `;
    const actionImages = action.images || [];
    if (actionImages.length) {
      const imageWrap = document.createElement("div");
      imageWrap.className = "action-media";
      actionImages.forEach((imageItem) => {
        const img = document.createElement("img");
        img.src = imageItem.src;
        img.alt = imageItem.alt || action.name;
        imageWrap.appendChild(img);
      });
      item.appendChild(imageWrap);
    }
    const actionLinks = action.video_links || [];
    if (actionLinks.length) {
      const linkWrap = document.createElement("div");
      linkWrap.className = "action-links";
      actionLinks.forEach((link) => {
        const a = document.createElement("a");
        a.href = link.url;
        a.target = "_blank";
        a.rel = "noreferrer";
        a.textContent = link.title;
        linkWrap.appendChild(a);
      });
      item.appendChild(linkWrap);
    }
    actionWrap.appendChild(item);
  });

  const links = document.getElementById("videoLinks");
  links.innerHTML = "";
  if (!detail.video_links.length) {
    links.innerHTML = '<span class="meta">暂无外部视频链接</span>';
  } else {
    detail.video_links.forEach((link) => {
      const a = document.createElement("a");
      a.href = link.url;
      a.target = "_blank";
      a.rel = "noreferrer";
      a.textContent = link.title;
      links.appendChild(a);
    });
  }

  document.getElementById("detailDialog").showModal();
}

async function loadStats() {
  const stats = await getJson("/api/stats");
  document.getElementById("totalDays").textContent = stats.total_checkin_days;
  document.getElementById("weekRate").textContent = `${stats.week_completed}/${stats.week_total}`;
  document.getElementById("streak").textContent = stats.current_streak;
}

async function init() {
  state.config = await getJson("/api/config");
  const today = isoDate(new Date());
  const start = state.config.start_date;
  state.selectedDate = today < start ? start : today;
  setVisibleMonth(parseLocalDate(state.selectedDate));
  await loadMonth();
  await loadDay(state.selectedDate);

  document.getElementById("prevMonth").addEventListener("click", async () => {
    setVisibleMonth(new Date(state.visibleDate.getFullYear(), state.visibleDate.getMonth() - 1, 1));
    await loadMonth();
  });

  document.getElementById("nextMonth").addEventListener("click", async () => {
    setVisibleMonth(new Date(state.visibleDate.getFullYear(), state.visibleDate.getMonth() + 1, 1));
    await loadMonth();
  });

  document.getElementById("closeDialog").addEventListener("click", () => {
    document.getElementById("detailDialog").close();
  });

  // Click outside dialog to close
  const detailDialog = document.getElementById("detailDialog");
  detailDialog.addEventListener("click", (e) => {
    if (e.target === detailDialog) {
      detailDialog.close();
    }
  });
}

init().catch((error) => {
  console.error(error);
  document.body.insertAdjacentHTML(
    "afterbegin",
    '<div style="padding:12px;background:#fee;color:#900">应用加载失败，请查看控制台。</div>'
  );
});
