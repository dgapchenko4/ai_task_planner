// Исправленная showTab
function showTab(t) {
    // Скрыть ВСЕ вкладки
    var allTabs = document.querySelectorAll('.tab-content');
    for (var i = 0; i < allTabs.length; i++) {
        allTabs[i].style.display = 'none';
    }
    
    // Показать нужную
    var target = document.getElementById('tab-' + t);
    if (target) target.style.display = 'block';
    
    // Подсветка кнопки
    var btns = document.querySelectorAll('.tab-btn');
    for (var j = 0; j < btns.length; j++) {
        btns[j].classList.remove('active');
    }
    var idx = { dash: 0, tasks: 1, cal: 2, settings: 3 }[t];
    if (idx !== undefined && btns[idx]) btns[idx].classList.add('active');
    
    // Загрузка данных
    if (t === 'dash') loadDashboard();
    if (t === 'tasks') loadTasks();
    if (t === 'cal') setTimeout(initCal, 300);
    if (t === 'settings') loadSettings();
}

// Переключение темы
function toggleTheme() {
    var isLight = document.getElementById('set-theme').checked;
    if (isLight) {
        document.body.classList.add('light-theme');
        localStorage.setItem('theme', 'light');
    } else {
        document.body.classList.remove('light-theme');
        localStorage.setItem('theme', 'dark');
    }
}

// Загрузка темы при старте
(function() {
    if (localStorage.getItem('theme') === 'light') {
        document.body.classList.add('light-theme');
    }
})();
var API = 'http://localhost:8000/api';
var token = localStorage.getItem('access_token');
var calendar = null;
var filterTag = null;

if (token) {
    console.log('Token found, checking...');
    fetch(API + '/auth/profile/', {
        headers: { 'Authorization': 'Bearer ' + token }
    })
    .then(function(r) {
        if (r.ok) {
            console.log('Token valid');
            showApp();
        } else {
            console.log('Token invalid');
            localStorage.clear();
            token = null;
            showAuth();
        }
    })
    .catch(function() {
        showAuth();
    });
} else {
    showAuth();
}

function showAuth() {
    document.getElementById('auth-page').style.display = 'flex';
    document.getElementById('app-page').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
}

function showApp() {
    document.getElementById('auth-page').style.display = 'none';
    document.getElementById('app-page').style.display = 'flex';
    showTab('dash');
    loadTags();
}

function showForm(f) {
    document.getElementById('login-form').style.display = (f === 'login') ? 'block' : 'none';
    document.getElementById('register-form').style.display = (f === 'register') ? 'block' : 'none';
}

function doLogin() {
    var err = document.getElementById('login-error');
    err.style.display = 'none';
    var email = document.getElementById('login-email').value.trim();
    var pass = document.getElementById('login-password').value;
    
    if (!email || !pass) {
        err.textContent = 'Заполните поля';
        err.style.display = 'block';
        return;
    }
    
    console.log('Logging in:', email);
    fetch(API + '/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, password: pass })
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        console.log('Login response:', d);
        if (d.access) {
            token = d.access;
            localStorage.setItem('access_token', token);
            localStorage.setItem('refresh_token', d.refresh);
            showApp();
        } else {
            err.textContent = 'Неверный email или пароль';
            err.style.display = 'block';
        }
    })
    .catch(function(e) {
        err.textContent = 'Ошибка соединения';
        err.style.display = 'block';
    });
}

function doRegister() {
    var err = document.getElementById('reg-error');
    err.style.display = 'none';
    
    var data = {
        username: document.getElementById('reg-user').value.trim(),
        first_name: document.getElementById('reg-first').value.trim(),
        last_name: document.getElementById('reg-last').value.trim(),
        email: document.getElementById('reg-email').value.trim(),
        password: document.getElementById('reg-pass1').value,
        password2: document.getElementById('reg-pass2').value
    };
    
    if (!data.username || !data.email || !data.password) {
        err.textContent = 'Заполните все поля';
        err.style.display = 'block';
        return;
    }
    if (data.password !== data.password2) {
        err.textContent = 'Пароли не совпадают';
        err.style.display = 'block';
        return;
    }
    
    console.log('Registering:', data.email);
    fetch(API + '/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.access) {
            token = d.access;
            localStorage.setItem('access_token', token);
            localStorage.setItem('refresh_token', d.refresh);
            showApp();
        } else {
            err.textContent = d.error || JSON.stringify(d);
            err.style.display = 'block';
        }
    })
    .catch(function(e) {
        err.textContent = 'Ошибка соединения';
        err.style.display = 'block';
    });
}

function doLogout() {
    token = null;
    localStorage.clear();
    if (calendar) { calendar.destroy(); calendar = null; }
    showAuth();
}

function showTab(t) {
    // Скрыть все вкладки
    var tabs = ['dash', 'tasks', 'cal', 'settings'];
    for (var i = 0; i < tabs.length; i++) {
        var el = document.getElementById('tab-' + tabs[i]);
        if (el) el.style.display = 'none';
    }
    // Показать нужную
    var target = document.getElementById('tab-' + t);
    if (target) target.style.display = 'block';
    
    // Подсветка кнопки
    var btns = document.querySelectorAll('.tab-btn');
    for (var j = 0; j < btns.length; j++) btns[j].classList.remove('active');
    var idx = { dash: 0, tasks: 1, cal: 2, settings: 3 }[t];
    if (idx !== undefined && btns[idx]) btns[idx].classList.add('active');
    
    if (t === 'dash') loadDashboard();
    if (t === 'tasks') loadTasks();
    if (t === 'cal') setTimeout(initCal, 300);
    if (t === 'settings') loadSettings();
}

function api(url, opt) {
    opt = opt || {};
    opt.headers = opt.headers || {};
    opt.headers['Content-Type'] = 'application/json';
    opt.headers['Authorization'] = 'Bearer ' + token;
    
    return fetch(API + url, opt).then(function(r) {
        if (r.status === 401) { doLogout(); throw new Error('Auth'); }
        if (r.status === 204) return {};
        return r.json();
    });
}

function loadTags() {
    api('/tasks/tasks/tags_list/').then(function(tags) {
        var c = document.getElementById('tags-list');
        if (!tags.length) { c.innerHTML = '<span style="color:#7a7a8c;font-size:10px;">нет</span>'; return; }
        c.innerHTML = tags.map(function(t) {
            return '<span style="background:' + (filterTag === t ? '#6C5CE7' : '#3a3a4f') + ';padding:3px 8px;border-radius:10px;font-size:10px;cursor:pointer;" onclick="setFilter(\'' + t + '\')">#' + t + '</span>';
        }).join('');
    }).catch(function(e) { console.error(e); });
}

function setFilter(tag) {
    filterTag = (filterTag === tag) ? null : tag;
    loadTags(); loadTasks(); loadDashboard();
}
function clearFilter() { filterTag = null; loadTags(); loadTasks(); loadDashboard(); }

function loadDashboard() {
    api('/tasks/tasks/statistics/').then(function(s) {
        document.getElementById('stats').innerHTML =
            '<div class="stat"><div class="n">' + (s.total || 0) + '</div><div class="l">Всего</div></div>' +
            '<div class="stat"><div class="n">' + ((s.pending || 0) + (s.in_progress || 0)) + '</div><div class="l">Активных</div></div>' +
            '<div class="stat"><div class="n">' + (s.completed || 0) + '</div><div class="l">Выполнено</div></div>' +
            '<div class="stat"><div class="n">' + (s.high_priority || 0) + '</div><div class="l">Срочных</div></div>';
        var url = '/tasks/tasks/'; if (filterTag) url += '?tag=' + filterTag;
        return api(url);
    }).then(function(tasks) {
        var list = Array.isArray(tasks) ? tasks.slice(0, 5) : (tasks.results || []).slice(0, 5);
        renderTasks(list, 'recent-tasks');
    }).catch(function(e) {});
}

function loadTasks() {
    var url = '/tasks/tasks/'; if (filterTag) url += '?tag=' + filterTag;
    api(url).then(function(tasks) {
        var list = Array.isArray(tasks) ? tasks : (tasks.results || []);
        renderTasks(list, 'all-tasks');
    }).catch(function(e) {});
}

function renderTasks(list, id) {
    var c = document.getElementById(id); if (!c) return;
    if (!list.length) { c.innerHTML = '<p style="color:#b0b0c0;text-align:center;padding:20px;">Нет задач</p>'; return; }
    c.innerHTML = list.map(function(t) {
        var p = { 'high': '🔥 Высокий', 'medium': '🟡 Средний', 'low': '🟢 Низкий' }[t.priority] || t.priority;
        return '<div class="task ' + (t.priority || 'medium') + '"><div class="row"><div><h4>' + (t.short_summary || t.title) + '</h4><p class="desc">' + (t.description || '') + '</p></div><div>' +
            (t.status !== 'completed' ? '<button onclick="doneTask(\'' + t.id + '\')" style="background:none;border:none;cursor:pointer;font-size:16px;">✅</button>' : '') +
            '<button onclick="editTask(\'' + t.id + '\')" style="background:none;border:none;cursor:pointer;font-size:16px;">✏️</button>' +
            '<button onclick="delTask(\'' + t.id + '\')" style="background:none;border:none;cursor:pointer;font-size:16px;">🗑️</button></div></div>' +
            '<div class="meta"><span>' + p + '</span>' + (t.estimated_duration ? '<span>⏱ ' + t.estimated_duration + ' мин</span>' : '') +
            (t.due_date ? '<span>📅 ' + new Date(t.due_date).toLocaleString('ru-RU', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' }) + '</span>' : '') + '</div>' +
            (t.tags && t.tags.length ? '<div class="tags">' + t.tags.map(function(tg) { return '<span onclick="setFilter(\'' + tg + '\')">#' + tg + '</span>'; }).join('') + '</div>' : '') + '</div>';
    }).join('');
}

function saveTask() {
    var id = document.getElementById('edit-id').value;
    var data = { title: document.getElementById('task-title').value.trim(), description: document.getElementById('task-desc').value.trim(), due_date: document.getElementById('task-due').value || null };
    if (!data.title) { alert('Введите заголовок'); return; }
    var p = id ? api('/tasks/tasks/' + id + '/', { method: 'PATCH', body: JSON.stringify(data) }) : api('/tasks/tasks/', { method: 'POST', body: JSON.stringify(data) });
    p.then(function() { closeModal(); loadDashboard(); loadTasks(); loadTags(); if (calendar) loadCalEvents(); }).catch(function(e) { alert(e.message); });
}

function editTask(id) {
    api('/tasks/tasks/' + id + '/').then(function(t) {
        document.getElementById('modal-title').textContent = '✏️ Редактировать';
        document.getElementById('edit-id').value = t.id;
        document.getElementById('task-title').value = t.title || '';
        document.getElementById('task-desc').value = t.description || '';
        document.getElementById('task-due').value = t.due_date ? new Date(t.due_date).toISOString().slice(0, 16) : '';
        document.getElementById('modal').classList.add('active');
    });
}

function delTask(id) { if (!confirm('Удалить?')) return; api('/tasks/tasks/' + id + '/', { method: 'DELETE' }).then(function() { loadDashboard(); loadTasks(); loadTags(); if (calendar) loadCalEvents(); }); }
function doneTask(id) { api('/tasks/tasks/' + id + '/mark_completed/', { method: 'POST' }).then(function() { loadDashboard(); loadTasks(); }); }

function openModal() {
    document.getElementById('modal-title').textContent = '📝 Новая задача';
    document.getElementById('edit-id').value = '';
    document.getElementById('task-title').value = '';
    document.getElementById('task-desc').value = '';
    document.getElementById('task-due').value = '';
    document.getElementById('modal').classList.add('active');
}
function closeModal() { document.getElementById('modal').classList.remove('active'); }

function initCal() {
    var el = document.getElementById('calendar'); if (!el) return; if (calendar) calendar.destroy();
    calendar = new FullCalendar.Calendar(el, {
        initialView: 'dayGridMonth', locale: 'ru', firstDay: 1, height: 'auto',
        headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek' },
        buttonText: { today: 'Сегодня', month: 'Месяц', week: 'Неделя' },
        eventClick: function(info) { if (confirm('Редактировать?')) editTask(info.event.id); }
    });
    calendar.render(); loadCalEvents();
}

function loadCalEvents() {
    if (!calendar) return;
    var url = '/tasks/tasks/'; if (filterTag) url += '?tag=' + filterTag;
    api(url).then(function(tasks) {
        var list = Array.isArray(tasks) ? tasks : (tasks.results || []);
        calendar.removeAllEvents();
        list.forEach(function(t) {
            if (t.due_date) calendar.addEvent({ id: t.id, title: t.short_summary || t.title || 'Задача', start: t.due_date, backgroundColor: t.priority === 'high' ? '#ff4444' : t.priority === 'medium' ? '#ffbb33' : '#00C851', borderColor: t.priority === 'high' ? '#ff4444' : t.priority === 'medium' ? '#ffbb33' : '#00C851', textColor: '#fff' });
        });
    }).catch(function(e) {});
}

function loadSettings() {
    api('/auth/notification-settings/').then(function(s) {
        document.getElementById('set-email').checked = s.email_notifications;
        document.getElementById('set-morning').checked = s.morning_summary;
        document.getElementById('set-morning-time').value = s.morning_summary_time || '08:00';
        document.getElementById('set-reminder').value = s.reminder_before_task || 30;
    }).catch(function(e) {});
}

function saveSettings() {
    var data = {
        email_notifications: document.getElementById('set-email').checked,
        morning_summary: document.getElementById('set-morning').checked,
        morning_summary_time: document.getElementById('set-morning-time').value,
        reminder_before_task: parseInt(document.getElementById('set-reminder').value)
    };
    fetch(API + '/auth/notification-settings/', { method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token }, body: JSON.stringify(data) })
        .then(function(r) { return r.json(); })
        .then(function() { var el = document.getElementById('settings-saved'); el.style.display = 'block'; setTimeout(function() { el.style.display = 'none'; }, 2000); });
}

console.log('Script loaded successfully!');

// ========== ПЕРЕКЛЮЧЕНИЕ ТЕМЫ ==========
function toggleTheme() {
    var isLight = document.getElementById('set-theme').checked;
    if (isLight) {
        document.body.classList.add('light-theme');
        localStorage.setItem('theme', 'light');
    } else {
        document.body.classList.remove('light-theme');
        localStorage.setItem('theme', 'dark');
    }
}

// Загрузка темы при старте
(function() {
    var savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        // Чекбокс обновится при загрузке настроек
    }
})();

// Обновим loadSettings для учета темы
var origLoadSettings = loadSettings;
loadSettings = function() {
    origLoadSettings();
    // Установим чекбокс темы
    var isLight = document.body.classList.contains('light-theme');
    var themeCheckbox = document.getElementById('set-theme');
    if (themeCheckbox) themeCheckbox.checked = isLight;
};

// Обновленная загрузка настроек
var origLoadSettings2 = loadSettings;
loadSettings = function() {
    if (typeof origLoadSettings2 === 'function') origLoadSettings2();
    
    // Установка темы
    var themeCheckbox = document.getElementById('set-theme');
    if (themeCheckbox) {
        themeCheckbox.checked = document.body.classList.contains('light-theme');
    }
    
    // Загрузка остальных настроек
    api('/auth/notification-settings/').then(function(s) {
        var emailEl = document.getElementById('set-email');
        var morningEl = document.getElementById('set-morning');
        var timeEl = document.getElementById('set-morning-time');
        var reminderEl = document.getElementById('set-reminder');
        
        if (emailEl) emailEl.checked = s.email_notifications;
        if (morningEl) morningEl.checked = s.morning_summary;
        if (timeEl) timeEl.value = s.morning_summary_time || '08:00';
        if (reminderEl) reminderEl.value = s.reminder_before_task || 30;
    }).catch(function(e) {});
};
