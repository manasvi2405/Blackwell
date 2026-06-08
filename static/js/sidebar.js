const sidebar = document.getElementById('sidebar');
const content = document.getElementById('content');
const toggleSidebarButton = document.getElementById('toggleSidebar');
const closeSidebarButton = document.getElementById('closeSidebar');

toggleSidebarButton.addEventListener('click', () => {
    sidebar.classList.toggle('active');            
});

closeSidebarButton.addEventListener('click', () => {
    sidebar.classList.remove('active');
});


