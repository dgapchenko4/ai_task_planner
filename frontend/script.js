const API = 'http://localhost:8000/api';
let token = localStorage.getItem('access_token');
let calendar = null;

// ========== ИНИЦИАЛИЗАЦИЯ ==========
document.addEventListener('DOMContentLoaded', function() {
    if (token) {
        document.getElementById('login-page').style.display = 'none';
        document.getElementById('app-page').style.display = 'block';
        showTab('dashboard');
    }
});

// ========== ЛОГИН ==========
async function login(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const err = document.getElementById('error');
    
    try {
        const res = await fetch(`${API}/auth/login/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        if (!res.ok) throw new Error('Неверный логин или пароль');
        
        const data = await res.json();
        token = data.access;
        localStorage.setItem('access_token', token);
        localStorage.setItem('refresh_token', data.refresh);
        
        document.getElementById('login-page').style.display = 'none';
        document.getElementById('app-page').style.display = 'block';
        showTab('dashboard');
    } catch(error) {
        err.textContent = error.message;
        err.style.display = 'block';
    }
}

function logout() {
    token = null;
    localStorage.clear();
    if (calendar) calendar.destroy();
    calendar = null;
    document.getElementById('login-page').style.display = 'flex';
    document.getElementById('app-page').style.display = 'none';
}

// ========== API ==========
async function api(url, opt = {}) {
    const res = await fetch(`${API}${url}`, {
        ...opt,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...opt.headers
        }
    });
    if (res.status === 401) { logout(); throw new Error('Unauthorized'); }
    if (res.status === 204) return {};
    return res.json();
}

// ========== НАВИГАЦИЯ ==========
function showTab(tab) {
    document.querySelectorAll('[id^="tab-"]').forEach(el => el.style.display = 'none');
    const tabEl = document.getElementById(`tab-${tab}`);
    if (tabEl) tabEl.style.display = 'block';
    
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const btnEl = document.getElementById(`btn-${tab}`);
    if (btnEl) btnEl.classList.add('active');
    
    if (tab === 'dashboard') loadDashboard();
    if (tab === 'tasks') loadTasks();
    if (tab === 'calendar') setTimeout(initCalendar, 200);
}

// ========== ДАШБОРД ==========
async function loadDashboard() {
    try {
        const stats = await api('/tasks/tasks/statistics/');
        document.getElementById('stats').innerHTML = `
            <div class="stat-box"><div class="num">${stats.total||0}</div><div class="lbl">Всего</div></div>
            <div class="stat-box"><div class="num">${(stats.pending||0)+(stats.in_progress||0)}</div><div class="lbl">Активных</div></div>
            <div class="stat-box"><div class="num">${stats.completed||0}</div><div class="lbl">Выполнено</div></div>
            <div class="stat-box"><div class="num">${stats.high_priority||0}</div><div class="lbl">Срочных</div></div>
        `;
        
        const tasks = await api('/tasks/tasks/');
        const list = Array.isArray(tasks) ? tasks.slice(0,5) : (tasks.results||[]).slice(0,5);
        renderTasks(list, 'recent');
    } catch(err) { console.error(err); }
}

// ========== ЗАДАЧИ ==========
async function loadTasks() {
    try {
        const tasks = await api('/tasks/tasks/');
        const list = Array.isArray(tasks) ? tasks : (tasks.results||[]);
        renderTasks(list, 'tasks');
    } catch(err) { console.error(err); }
}

function renderTasks(list, containerId) {
    const c = document.getElementById(containerId);
    if (!c) return;
    if (!list.length) { c.innerHTML = '<p style="color:#b0b0c0;padding:20px;">Нет задач</p>'; return; }
    
    c.innerHTML = list.map(t => `
        <div class="task-card ${t.priority||'medium'}" id="task-${t.id}">
            <div class="task-card-header">
                <div>
                    <h4>${t.short_summary || t.title || 'Без названия'}</h4>
                    <p>${t.description||''}</p>
                </div>
                <div class="task-card-actions">
                    ${t.status!=='completed' ? `<button onclick="completeTask('${t.id}')" title="Выполнено">✅</button>` : ''}
                    <button onclick="editTask('${t.id}')" title="Редактировать">✏️</button>
                    <button onclick="deleteTask('${t.id}')" title="Удалить">🗑️</button>
                </div>
            </div>
            <div class="task-meta">
                <span class="priority-badge ${t.priority}">${t.priority==='high'?'🔥 Высокий':t.priority==='medium'?'🟡 Средний':'🟢 Низкий'}</span>
                ${t.estimated_duration?`<span>⏱ ${t.estimated_duration} мин</span>`:''}
                ${t.due_date?`<span>📅 ${new Date(t.due_date).toLocaleString('ru-RU', {day:'numeric',month:'long',hour:'2-digit',minute:'2-digit'})}</span>`:''}
                <span>${t.status==='completed'?'✅ Выполнена':'📌 В работе'}</span>
            </div>
            ${t.tags&&t.tags.length?`<div class="task-tags">${t.tags.map(tag=>`<span class="tag">#${tag}</span>`).join('')}</div>`:''}
        </div>
    `).join('');
}

// ========== СОХРАНИТЬ (СОЗДАТЬ ИЛИ ОБНОВИТЬ) ==========
async function saveTask(e) {
    e.preventDefault();
    
    const taskId = document.getElementById('task-id').value;
    const title = document.getElementById('task-title').value.trim();
    const desc = document.getElementById('task-desc').value.trim();
    const due = document.getElementById('task-due').value;
    
    if (!title) { alert('Введите заголовок'); return; }
    
    const data = { title, description: desc, due_date: due || null };
    
    try {
        if (taskId) {
            // РЕДАКТИРОВАНИЕ существующей задачи
            console.log('Updating task:', taskId, data);
            await api(`/tasks/tasks/${taskId}/`, { 
                method: 'PUT',  // PUT вместо PATCH - полное обновление
                body: JSON.stringify(data) 
            });
        } else {
            // СОЗДАНИЕ новой задачи
            console.log('Creating task:', data);
            await api('/tasks/tasks/', { 
                method: 'POST', 
                body: JSON.stringify(data) 
            });
        }
        
        closeModal();
        refreshAll();
    } catch(err) { 
        console.error('Save error:', err);
        alert('Ошибка сохранения: '+err.message); 
    }
}

// ========== РЕДАКТИРОВАТЬ ==========
async function editTask(id) {
    try {
        const task = await api(`/tasks/tasks/${id}/`);
        document.getElementById('modal-title').textContent = '✏️ Редактировать задачу';
        document.getElementById('task-id').value = task.id;
        document.getElementById('task-title').value = task.title || '';
        document.getElementById('task-desc').value = task.description || '';
        
        if (task.due_date) {
            // Форматируем дату для input datetime-local
            const d = new Date(task.due_date);
            const pad = (n) => String(n).padStart(2, '0');
            document.getElementById('task-due').value = 
                `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
        } else {
            document.getElementById('task-due').value = '';
        }
        
        document.getElementById('modal').style.display = 'flex';
    } catch(err) {
        alert('Ошибка загрузки задачи: '+err.message);
    }
}

// ========== УДАЛИТЬ ==========
async function deleteTask(id) {
    if (!confirm('Удалить задачу?')) return;
    try {
        await api(`/tasks/tasks/${id}/`, { method: 'DELETE' });
        
        // Удаляем из DOM сразу
        const el = document.getElementById(`task-${id}`);
        if (el) el.remove();
        
        // Обновляем все виды
        refreshAll();
    } catch(err) { console.error('Delete error:', err); }
}

async function completeTask(id) {
    try {
        await api(`/tasks/tasks/${id}/mark_completed/`, { method: 'POST' });
        refreshAll();
    } catch(err) { console.error(err); }
}

// ========== ОБНОВИТЬ ВСЕ ==========
function refreshAll() {
    loadDashboard();
    
    const activeTab = document.querySelector('.tab-btn.active')?.id;
    if (activeTab === 'btn-tasks') loadTasks();
    if (activeTab === 'btn-calendar' && calendar) loadCalendarEvents();
    
    // Всегда обновляем календарь если он есть
    if (calendar) loadCalendarEvents();
}

// ========== МОДАЛЬНОЕ ОКНО ==========
function openModal() {
    document.getElementById('modal-title').textContent = '📝 Новая задача';
    document.getElementById('task-id').value = '';
    document.getElementById('task-title').value = '';
    document.getElementById('task-desc').value = '';
    document.getElementById('task-due').value = '';
    document.getElementById('modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

// Закрытие по клику на фон
document.addEventListener('click', function(e) {
    if (e.target.id === 'modal') closeModal();
});

// ========== КАЛЕНДАРЬ ==========
function initCalendar() {
    const el = document.getElementById('calendar');
    if (!el) return;
    
    if (calendar) {
        calendar.destroy();
        calendar = null;
    }
    
    calendar = new FullCalendar.Calendar(el, {
        initialView: 'dayGridMonth',
        locale: 'ru',
        firstDay: 1,
        height: 'auto',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },
        buttonText: { today: 'Сегодня', month: 'Месяц', week: 'Неделя' },
        events: [],
        eventClick: function(info) {
            showEventMenu(info.event, info.jsEvent);
        }
    });
    
    calendar.render();
    loadCalendarEvents();
}

function showEventMenu(event, jsEvent) {
    // Удаляем старое меню
    const old = document.getElementById('event-menu');
    if (old) old.remove();
    
    const menu = document.createElement('div');
    menu.id = 'event-menu';
    menu.style.cssText = `
        position: fixed; background: #2d2d3f; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 8px; z-index: 10000;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); min-width: 200px;
    `;
    
    const p = event.extendedProps.priority || 'medium';
    const ptext = p === 'high' ? '🔥 Высокий' : p === 'medium' ? '🟡 Средний' : '🟢 Низкий';
    const start = event.start;
    
    menu.innerHTML = `
        <div style="padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.05);">
            <h4 style="margin:0 0 4px 0;color:#fff;">${event.title}</h4>
            <p style="margin:0;color:#b0b0c0;font-size:12px;">
                ${start ? '📅 '+start.toLocaleDateString('ru-RU',{day:'numeric',month:'long',year:'numeric'}) : ''}
                ${start ? ' 🕐 '+start.toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'}) : ''}
            </p>
            <p style="margin:4px 0 0;font-size:12px;">${ptext}</p>
        </div>
        <button onclick="editTask('${event.id}');closeEventMenu();" 
            style="width:100%;padding:10px;background:transparent;border:none;color:#fff;text-align:left;cursor:pointer;border-radius:8px;font-size:14px;"
            onmouseover="this.style.background='#3a3a4f'" onmouseout="this.style.background='transparent'">
            ✏️ Редактировать
        </button>
        <button onclick="deleteTask('${event.id}');closeEventMenu();" 
            style="width:100%;padding:10px;background:transparent;border:none;color:#FF4444;text-align:left;cursor:pointer;border-radius:8px;font-size:14px;"
            onmouseover="this.style.background='rgba(255,68,68,0.1)'" onmouseout="this.style.background='transparent'">
            🗑️ Удалить
        </button>
        ${event.extendedProps.status !== 'completed' ? `
        <button onclick="completeTask('${event.id}');closeEventMenu();" 
            style="width:100%;padding:10px;background:transparent;border:none;color:#00C851;text-align:left;cursor:pointer;border-radius:8px;font-size:14px;"
            onmouseover="this.style.background='rgba(0,200,81,0.1)'" onmouseout="this.style.background='transparent'">
            ✅ Выполнено
        </button>` : ''}
    `;
    
    menu.style.left = Math.min(jsEvent.clientX, window.innerWidth - 220) + 'px';
    menu.style.top = Math.min(jsEvent.clientY, window.innerHeight - 200) + 'px';
    
    document.body.appendChild(menu);
    
    setTimeout(() => {
        document.addEventListener('click', function closeMenu(e) {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        });
    }, 10);
}

function closeEventMenu() {
    const menu = document.getElementById('event-menu');
    if (menu) menu.remove();
}

async function loadCalendarEvents() {
    if (!calendar) return;
    
    try {
        const tasks = await api('/tasks/tasks/');
        const list = Array.isArray(tasks) ? tasks : (tasks.results||[]);
        
        // Удаляем ВСЕ события
        calendar.removeAllEvents();
        
        // Добавляем заново
        list.forEach(t => {
            if (t.due_date) {
                calendar.addEvent({
                    id: t.id,
                    title: t.short_summary || t.title || 'Задача',
                    start: t.due_date,
                    backgroundColor: t.priority==='high'?'#FF4444':t.priority==='medium'?'#FFBB33':'#00C851',
                    borderColor: t.priority==='high'?'#FF4444':t.priority==='medium'?'#FFBB33':'#00C851',
                    textColor: '#fff',
                    extendedProps: {
                        priority: t.priority,
                        status: t.status,
                        description: t.description,
                        tags: t.tags
                    }
                });
            }
        });
        
        console.log('Calendar updated:', list.length, 'tasks');
    } catch(err) { 
        console.error('Calendar load error:', err); 
    }
}
