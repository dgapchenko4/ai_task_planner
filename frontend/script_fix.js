function showTab(t) {
    var tabs = document.querySelectorAll('.tab-content');
    for (var i = 0; i < tabs.length; i++) tabs[i].style.display = 'none';
    var target = document.getElementById('tab-' + t);
    if (target) target.style.display = 'block';
    var btns = document.querySelectorAll('.tab-btn');
    for (var j = 0; j < btns.length; j++) btns[j].classList.remove('active');
    var idx = {dash:0,tasks:1,cal:2,settings:3}[t];
    if (idx !== undefined && btns[idx]) btns[idx].classList.add('active');
    if (t==='dash') loadDashboard();
    if (t==='tasks') loadTasks();
    if (t==='cal') setTimeout(initCal,300);
    if (t==='settings') loadSettings();
}
function toggleTheme() {
    var isLight = document.getElementById('set-theme').checked;
    document.body.classList.toggle('light-theme', isLight);
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
}
(function() {
    if (localStorage.getItem('theme') === 'light') document.body.classList.add('light-theme');
})();
