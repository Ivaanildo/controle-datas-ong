// Central ONG - Sistema de Controle de Validades
// JavaScript Principal

// Estado global da aplicação
if (typeof appState === 'undefined') {
    var appState = {
        currentView: 'dashboard-view',
        produtos: [],
        categorias: [],
        movimentacoes: [],
        charts: {},
        currentPageMovements: 1, // Adicionado para controlar a página atual das movimentações
        currentPageProducts: 1 // Adicionado para controlar a página atual dos produtos
    };
}

// Função centralizada para atualizar dados e visualizações
async function refreshAppData() {
    console.log('🔄 Iniciando refreshAppData...');
    try {
        await loadInitialData();
        console.log('🔄 refreshAppData executado com sucesso!');
    } catch (error) {
        console.error('❌ Erro em refreshAppData:', error);
        showToast('Erro ao atualizar dados', 'error');
    }
}

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    initNavigation();
    await loadInitialData();
    initModals();
    initFilters();
    initGlobalSearch();
    setupForms();
    showView(appState.currentView); // Ensure the initial view is correctly displayed
}

// Navegação
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const view = this.dataset.view;
            if (view) {
                showView(view);
            }
        });
    });
}

function showView(viewName) {
    // Mapeamento de IDs de views para garantir que todas sejam ocultadas
    const allViewIds = [
        'dashboard-view',
        'products-view',
        'categories-view',
        'movements-view',
        'reports-view',
        'validity-management-view'
    ];

    // Ocultar todas as views conhecidas e remover a classe active
    allViewIds.forEach(id => {
        const view = document.getElementById(id);
        if (view) {
            view.classList.remove('active');
            view.style.display = 'none'; // Esconder explicitamente
        }
    });
    
    // Remover classe active de todos os nav-items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Mostrar view selecionada e adicionar a classe active
    const targetView = document.getElementById(viewName);
    if (targetView) {
        targetView.classList.add('active');
        targetView.style.display = 'block'; // Mostrar explicitamente
    }
    
    // Adicionar classe active ao nav-item correspondente
    const navItem = document.querySelector(`[data-view="${viewName}"]`);
    if (navItem) {
        navItem.classList.add('active');
    }
    
    // Atualizar título da página
    const titles = {
        'dashboard-view': 'Dashboard',
        'products-view': 'Produtos',
        'categories-view': 'Categorias',
        'movements-view': 'Movimentações',
        'reports-view': 'Relatórios',
        'validity-management-view': 'Controle de Validades'
    };
    
    document.getElementById('pageTitle').textContent = titles[viewName] || 'Central ONG';
    
    // Atualizar estado
    appState.currentView = viewName;
    
    // Carregar dados específicos da view
    if (viewName === 'dashboard-view') {
        updateDashboard();
    } else {
        loadViewData(viewName);
    }
}

function loadViewData(viewName) {
    console.log(`Carregando dados para a view: ${viewName}`); // Adicionando log
    switch(viewName) {
        case 'dashboard-view':
            updateDashboard();
            break;
        case 'products-view':
            loadProductsTable();
            break;
        case 'categories-view':
            loadCategoriesTable();
            break;
        case 'movements-view':
            loadMovementsTable();
            break;
        case 'validity-management-view':
            loadValidityTable();
            break;
        case 'reports-view':
            updateReportsView();
            break;
    }
}

function updateReportsView() {
    const reportsGrid = document.querySelector('.reports-grid');
    const emptyState = document.getElementById('reports-empty-state');

    if (!reportsGrid || !emptyState) return;

    // Verifica se há produtos, categorias ou movimentações cadastradas
    if (appState.produtos.length === 0 && appState.categorias.length === 0 && appState.movimentacoes.length === 0) {
        reportsGrid.style.display = 'none';
        emptyState.style.display = 'block';
    } else {
        reportsGrid.style.display = 'grid'; // Ou 'block', dependendo do display original
        emptyState.style.display = 'none';
    }
}

// Sidebar Toggle
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Carregar dados iniciais
async function loadInitialData() {
    try {
        console.log('📥 Carregando dados iniciais...');
        
        // Carregar categorias
        const categoriasResponse = await fetch('/api/categorias');
        appState.categorias = await categoriasResponse.json();
        console.log(`📂 ${appState.categorias.length} categorias carregadas`);
        
        // Carregar produtos
        const produtosResponse = await fetch('/api/produtos');
        const produtosData = await produtosResponse.json();
        appState.produtos = Array.isArray(produtosData.produtos) ? produtosData.produtos : [];
        console.log(`📦 ${appState.produtos.length} produtos carregados`);
        
        // Debug: mostrar produtos e seus status
        if (appState.produtos.length > 0) {
            console.log('Status dos produtos:', appState.produtos.map(p => ({
                nome: p.nome,
                validade: p.data_validade,
                dias_restantes: p.dias_restantes,
                status: p.status_validade
            })));
        }
        
        // Carregar movimentações
        const movimentacoesResponse = await fetch('/api/movimentacoes');
        appState.movimentacoes = await movimentacoesResponse.json();
        console.log(`📋 ${appState.movimentacoes.length} movimentações carregadas`);
        
        // Carregar opções nos selects
        loadCategoryOptions();
        loadProductOptions();
        
        console.log('✅ Dados carregados com sucesso!');
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        showToast('Erro ao carregar dados do sistema', 'error');
    }
}

function loadCategoryOptions() {
    const selects = document.querySelectorAll('#product-category, #filtroCategoria, #categoryReportFilter');
    selects.forEach(select => {
        // Limpar opções existentes (exceto a primeira)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Adicionar categorias
        appState.categorias.forEach(categoria => {
            const option = document.createElement('option');
            option.value = categoria.id;
            option.textContent = categoria.nome;
            select.appendChild(option);
        });
    });
}

function loadProductOptions() {
    const selects = document.querySelectorAll('#movement-product, #filtroMovimentoProduto');
    selects.forEach(select => {
        // Limpar opções existentes (exceto a primeira)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        // Adicionar apenas produtos com estoque > 0
        appState.produtos.filter(produto => produto.quantidade_atual > 0).forEach(produto => {
            const option = document.createElement('option');
            option.value = produto.id;
            option.textContent = `${produto.nome} (${produto.quantidade_atual} ${produto.unidade})`;
            select.appendChild(option);
        });
    });
}

// Dashboard
function updateDashboard() {
    updateStatusCards();
    updateUpcomingExpiryTable();
    updateCategoryChart();
    updateProductStatusChart();
    console.log('🟢 updateDashboard OK'); // Teste
}

async function updateStatusCards() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const stats = await response.json();

        const vencidosEl = document.getElementById('vencidos-count');
        if (vencidosEl) vencidosEl.textContent = stats.vencidos || 0;

        const seteDiasEl = document.getElementById('sete-dias-count');
        if (seteDiasEl) seteDiasEl.textContent = stats.sete_dias || 0;

        const trintaDiasEl = document.getElementById('trinta-dias-count');
        if (trintaDiasEl) trintaDiasEl.textContent = stats.trinta_dias || 0;

    } catch (error) {
        console.error('❌ Erro ao atualizar status cards:', error);
        showToast('Erro ao carregar estatísticas', 'error');
    }
}

function updateUpcomingExpiryTable() {
    const tbody = document.getElementById('upcoming-expiry-table');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    // Filtrar produtos próximos ao vencimento (30 dias)
    const hoje = new Date();
    const produtosProximos = appState.produtos.filter(p => {
        const dataValidade = new Date(p.data_validade);
        const dias = Math.ceil((dataValidade - hoje) / (1000 * 60 * 60 * 24));
        return dias <= 30;
    }).sort((a, b) => new Date(a.data_validade) - new Date(b.data_validade));
    
    produtosProximos.forEach(produto => {
        const categoria = appState.categorias.find(c => c.id === produto.categoria_id);
        const dataValidade = new Date(produto.data_validade);
        const diasRestantes = Math.ceil((dataValidade - hoje) / (1000 * 60 * 60 * 24));
        const status = getValidityStatus(diasRestantes);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${produto.nome}</td>
            <td>${categoria ? categoria.nome : 'N/A'}</td>
            <td>${formatDate(produto.data_validade)}</td>
            <td>${diasRestantes}</td>
            <td>${produto.quantidade_atual} ${produto.unidade}</td>
            <td><span class="status-badge ${status}">${getStatusText(status)}</span></td>
        `;
        tbody.appendChild(row);
    });
}

function updateCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    // Verificação de dados válidos
    if (!Array.isArray(appState.categorias) || appState.categorias.length === 0 ||
        !Array.isArray(appState.produtos) || appState.produtos.length === 0) {
        console.warn('Dados insuficientes para renderizar o gráfico de categorias.');
        return;
    }

    if (appState.charts.category) {
        appState.charts.category.destroy();
    }

    const data = appState.categorias.map(categoria => ({
        label: categoria.nome,
        count: appState.produtos.filter(p => p.categoria_id === categoria.id).length
    }));

    // Paleta de cores harmoniosas e distintas para categorias
    const categoryColors = [
        '#06b6d4', // Azul ciano (primary)
        '#10b981', // Verde (success)
        '#f59e0b', // Amarelo/Laranja (warning)
        '#8b5cf6', // Púrpura
        '#ef4444', // Vermelho (danger)
        '#3b82f6', // Azul (info)
        '#ec4899', // Rosa
        '#f97316', // Laranja
        '#84cc16', // Verde lima
        '#6366f1'  // Índigo
    ];

    appState.charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.label),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: categoryColors.slice(0, data.length),
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} produtos (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    console.log('🟢 updateCategoryChart OK');
}

async function updateProductStatusChart() {
    const ctx = document.getElementById('productStatusChart');
    if (!ctx) {
        console.warn('⚠️ Elemento productStatusChart não encontrado');
        return;
    }

    if (appState.charts.productStatus) {
        appState.charts.productStatus.destroy();
    }

    try {
        console.log('📊 Buscando dados do gráfico de status...');
        const response = await fetch('/api/dashboard/product-status-chart');
        const data = await response.json();
        
        console.log('📊 Dados do gráfico recebidos:', data);

        const labels = Object.keys(data);
        const values = Object.values(data);
        
        // Cores consistentes com os cards de status - LÓGICA FINAL
        const colors = {
            'Vencidos': '#ef4444',                           // 🔴 Vermelho (var(--danger-color))
            'Vencem em 7 dias': '#f59e0b',                   // 🟡 Amarelo (var(--warning-color))
            'Vencem em 30 dias': '#10b981'                                  // 🟢 Verde (var(--success-color))
        };
        
        const chartColors = labels.map(label => colors[label] || '#6b7280');

        console.log('📊 Labels:', labels);
        console.log('📊 Values:', values);
        console.log('📊 Colors:', chartColors);

        appState.charts.productStatus = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Status dos Produtos',
                    data: values,
                    backgroundColor: chartColors,
                    borderColor: '#ffffff',
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        console.log('🟢 updateProductStatusChart OK');
    } catch (error) {
        console.error('❌ Erro ao atualizar gráfico de status de produtos:', error);
    }
}

// Produtos
async function loadProductsTable() {
    const tbody = document.getElementById('products-table-body');
    const productsTable = document.getElementById('productsTable');
    const emptyState = document.getElementById('products-empty-state');
    const paginationControls = document.getElementById('products-pagination');
    const pageInfo = document.getElementById('products-page-info');
    const prevPageBtn = document.getElementById('products-prev-page');
    const nextPageBtn = document.getElementById('products-next-page');

    if (!tbody || !productsTable || !emptyState || !paginationControls || !pageInfo || !prevPageBtn || !nextPageBtn) return;
    
    tbody.innerHTML = '';

    // Coletar filtros
    const search = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const categoria = document.getElementById('filtroCategoria')?.value || '';
    const quantidade = document.getElementById('filtroQuantidade')?.value || '';
    const status = document.getElementById('filtroStatus')?.value || '';

    let url = `/api/produtos?page=${appState.currentPageProducts}&per_page=10`;
    if (search) url += `&nome=${search}`;
    if (categoria) url += `&categoria_id=${categoria}`;
    if (quantidade) url += `&quantidade=${quantidade}`;
    if (status) url += `&status=${status}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.produtos.length === 0) {
            productsTable.style.display = 'none';
            emptyState.style.display = 'block';
            paginationControls.style.display = 'none';
        } else {
            productsTable.style.display = 'table';
            emptyState.style.display = 'none';
            paginationControls.style.display = 'flex';

            data.produtos.forEach(produto => {
                const categoria = appState.categorias.find(c => c.id === produto.categoria_id);
                const hoje = new Date();
                const diasRestantes = Math.ceil((new Date(produto.data_validade) - hoje) / (1000 * 60 * 60 * 24));
                const status = getValidityStatus(diasRestantes);
                const valorTotal = produto.quantidade_atual * produto.valor_unitario;
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><span class="status-badge ${status}">${getStatusText(status)}</span></td>
                    <td>${produto.nome}</td>
                    <td>${categoria ? categoria.nome : 'N/A'}</td>
                    <td>${formatDate(produto.data_validade)}</td>
                    <td>${diasRestantes}</td>
                    <td>${produto.quantidade_atual} ${produto.unidade}</td>
                    <td>R$ ${valorTotal.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="editProduct(${produto.id})">✏️</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteProduct(${produto.id})">🗑️</button>
                    </td>
                `;
                tbody.appendChild(row);
            });

            // Atualizar controles de paginação
            pageInfo.textContent = `Página ${data.current_page} de ${data.total_pages} (${data.total_items} itens)`;
            prevPageBtn.disabled = data.current_page === 1;
            nextPageBtn.disabled = data.current_page === data.total_pages;

            // Remover e adicionar listeners para evitar duplicação
            prevPageBtn.removeEventListener('click', handlePrevPageProducts);
            nextPageBtn.removeEventListener('click', handleNextPageProducts);
            prevPageBtn.addEventListener('click', handlePrevPageProducts);
            nextPageBtn.addEventListener('click', handleNextPageProducts);
        }
    } catch (error) {
        console.error('❌ Erro ao carregar produtos:', error);
        showToast('Erro ao carregar produtos', 'error');
    }
}

function handlePrevPageProducts() {
    if (appState.currentPageProducts > 1) {
        appState.currentPageProducts--;
        loadProductsTable();
    }
}

function handleNextPageProducts() {
    // A verificação de total_pages será feita dentro de loadProductsTable
    appState.currentPageProducts++;
    loadProductsTable();
}

function applyProductFilters() {
    appState.currentPageProducts = 1; // Resetar para a primeira página ao aplicar filtros
    loadProductsTable();
}

function clearProductFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('filtroCategoria').value = '';
    document.getElementById('filtroQuantidade').value = '';
    document.getElementById('filtroStatus').value = '';
    appState.currentPageProducts = 1;
    loadProductsTable();
}

// Categorias
function loadCategoriesTable() {
    const tbody = document.getElementById('categories-table-body');
    const categoriesTable = tbody.closest('table');
    const emptyState = document.getElementById('categories-empty-state');

    if (!tbody || !categoriesTable || !emptyState) return;
    
    tbody.innerHTML = '';
    
    if (appState.categorias.length === 0) {
        categoriesTable.style.display = 'none';
        emptyState.style.display = 'block';
    } else {
        categoriesTable.style.display = 'table';
        emptyState.style.display = 'none';
        appState.categorias.forEach(categoria => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${categoria.nome}</td>
                <td>${categoria.descricao || 'N/A'}</td>
                <td>${categoria.produtos_count}</td>
                <td>${formatDate(categoria.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editCategory(${categoria.id})">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteCategory(${categoria.id})">🗑️</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
}

// Movimentações
async function loadMovementsTable() {
    const tbody = document.getElementById('movements-table-body');
    const movementsTable = tbody.closest('table');
    const emptyState = document.getElementById('movements-empty-state');
    const paginationControls = document.getElementById('movements-pagination');
    const pageInfo = document.getElementById('movements-page-info');
    const prevPageBtn = document.getElementById('movements-prev-page');
    const nextPageBtn = document.getElementById('movements-next-page');

    if (!tbody || !movementsTable || !emptyState || !paginationControls || !pageInfo || !prevPageBtn || !nextPageBtn) return;

    tbody.innerHTML = '';

    // Coletar filtros
    const filtroProdutoId = document.getElementById('filtroMovimentoProduto')?.value;
    const filtroTipo = document.getElementById('filtroMovimentoTipo')?.value;
    const filtroMotivo = document.getElementById('filtroMovimentoMotivo')?.value;
    const filtroDataInicio = document.getElementById('filtroMovimentoDataInicio')?.value;
    const filtroDataFim = document.getElementById('filtroMovimentoDataFim')?.value;
    const filtroUsuario = document.getElementById('filtroMovimentoUsuario')?.value;

    let url = `/api/movimentacoes?page=${appState.currentPageMovements}&per_page=10`;
    if (filtroProdutoId) url += `&produto_id=${filtroProdutoId}`;
    if (filtroTipo) url += `&tipo=${filtroTipo}`;
    if (filtroMotivo) url += `&motivo=${filtroMotivo}`;
    if (filtroDataInicio) url += `&data_inicio=${filtroDataInicio}`;
    if (filtroDataFim) url += `&data_fim=${filtroDataFim}`;
    if (filtroUsuario) url += `&usuario=${filtroUsuario}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.movimentacoes.length === 0) {
            movementsTable.style.display = 'none';
            emptyState.style.display = 'block';
            paginationControls.style.display = 'none';
        } else {
            movementsTable.style.display = 'table';
            emptyState.style.display = 'none';
            paginationControls.style.display = 'flex';

            data.movimentacoes.forEach(mov => {
                const produto = appState.produtos.find(p => p.id === mov.produto_id);
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${formatDate(mov.data_movimentacao)}</td>
                    <td>${produto ? produto.nome : 'N/A'}</td>
                    <td><span class="status-badge ${mov.tipo}">${mov.tipo}</span></td>
                    <td>${mov.quantidade}</td>
                    <td>${mov.motivo}</td>
                    <td>${mov.usuario}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="editMovement(${mov.id})">✏️</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteMovement(${mov.id})">🗑️</button>
                    </td>
                `;
                tbody.appendChild(row);
            });

            // Atualizar controles de paginação
            pageInfo.textContent = `Página ${data.current_page} de ${data.total_pages} (${data.total_items} itens)`;
            prevPageBtn.disabled = data.current_page === 1;
            nextPageBtn.disabled = data.current_page === data.total_pages;

            // Remover e adicionar listeners para evitar duplicação
            prevPageBtn.removeEventListener('click', handlePrevPageMovements);
            nextPageBtn.removeEventListener('click', handleNextPageMovements);
            prevPageBtn.addEventListener('click', handlePrevPageMovements);
            nextPageBtn.addEventListener('click', handleNextPageMovements);
        }
    } catch (error) {
        console.error('❌ Erro ao carregar movimentações:', error);
        showToast('Erro ao carregar movimentações', 'error');
    }
    console.log('🟢 loadMovementsTable OK');
}

function handlePrevPageMovements() {
    if (appState.currentPageMovements > 1) {
        appState.currentPageMovements--;
        loadMovementsTable();
    }
}

function handleNextPageMovements() {
    // A verificação de total_pages será feita dentro de loadMovementsTable
    appState.currentPageMovements++;
    loadMovementsTable();
}

function applyMovementFilters() {
    appState.currentPageMovements = 1; // Resetar para a primeira página ao aplicar filtros
    loadMovementsTable();
}

function clearMovementFilters() {
    document.getElementById('filtroMovimentoProduto').value = '';
    document.getElementById('filtroMovimentoTipo').value = '';
    document.getElementById('filtroMovimentoMotivo').value = '';
    document.getElementById('filtroMovimentoDataInicio').value = '';
    document.getElementById('filtroMovimentoDataFim').value = '';
    document.getElementById('filtroMovimentoUsuario').value = '';
    appState.currentPageMovements = 1;
    loadMovementsTable();
}

// Controle de Validades
function loadValidityTable() {
    const tbody = document.getElementById('validity-table-body');
    const validityTable = tbody.closest('table');
    const emptyState = document.getElementById('validity-empty-state');

    if (!tbody || !validityTable || !emptyState) return;
    
    tbody.innerHTML = '';
    
    // A lógica de exibição da tabela de validades é um pouco diferente
    // pois ela filtra produtos. Se não houver produtos após o filtro,
    // o empty state deve aparecer.
    const produtosComValidade = appState.produtos.filter(p => p.data_validade);

    if (produtosComValidade.length === 0) {
        validityTable.style.display = 'none';
        emptyState.style.display = 'block';
    } else {
        validityTable.style.display = 'table';
        emptyState.style.display = 'none';
        // Usar a mesma lógica da tabela de produtos para preencher
        // mas apenas para produtos com data de validade
        produtosComValidade.forEach(produto => {
            const categoria = appState.categorias.find(c => c.id === produto.categoria_id);
            const hoje = new Date();
            const diasRestantes = Math.ceil((new Date(produto.data_validade) - hoje) / (1000 * 60 * 60 * 24));
            const status = getValidityStatus(diasRestantes);
            const valorTotal = produto.quantidade_atual * produto.valor_unitario;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="status-badge ${status}">${getStatusText(status)}</span></td>
                <td>${produto.nome}</td>
                <td>${categoria ? categoria.nome : 'N/A'}</td>
                <td>${formatDate(produto.data_validade)}</td>
                <td>${diasRestantes}</td>
                <td>${produto.quantidade_atual} ${produto.unidade}</td>
                <td>R$ ${valorTotal.toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editProduct(${produto.id})">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteProduct(${produto.id})">🗑️</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
}

// Modais
function initModals() {
    // Fechar modais quando clicar no overlay
    document.querySelectorAll('.overlay').forEach(overlay => {
        overlay.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });
    
    // Fechar modais com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal.id);
            }
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Limpar formulário
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
    }
}

// Formulários
function setupForms() {
    // Formulário de produto
    const productForm = document.getElementById('product-form');
    if (productForm) {
        productForm.addEventListener('submit', handleProductSubmit);
    }
    
    // Formulário de categoria
    const categoryForm = document.getElementById('category-form');
    if (categoryForm) {
        categoryForm.addEventListener('submit', handleCategorySubmit);
    }
    
    // Formulário de movimentação
    const movementForm = document.getElementById('movement-form');
    if (movementForm) {
        movementForm.addEventListener('submit', handleMovementSubmit);
    }
}

function handleProductSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const produto = {
        nome: formData.get('nome'),
        descricao: formData.get('descricao'),
        quantidade_inicial: parseInt(formData.get('quantidade_inicial')),
        quantidade_atual: parseInt(formData.get('quantidade_inicial')),
        unidade: formData.get('unidade'),
        data_validade: formData.get('data_validade'),
        valor_unitario: parseFloat(formData.get('valor_unitario')),
        categoria_id: parseInt(formData.get('categoria_id')),
        localizacao: formData.get('localizacao'),
        codigo_barras: formData.get('codigo_barras'),
        status: 'ativo'
    };
    fetch('/api/produtos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(produto)
    })
    .then(res => res.json())
    .then(novoProduto => {
        const movimento = {
            produto_id: novoProduto.id,
            tipo: 'entrada',
            quantidade: novoProduto.quantidade_inicial,
            motivo: 'Cadastro inicial',
            usuario: 'Admin'
        };
        return fetch('/api/movimentacoes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(movimento)
        });
    })
    .then(() => {
        showToast('Produto cadastrado com sucesso!', 'success');
        closeModal('product-modal');
        refreshAppData();
        console.log('🟢 handleProductSubmit OK'); // Teste
    })
    .catch(err => {
        showToast('Erro ao cadastrar produto', 'error');
        console.error('❌ handleProductSubmit erro:', err);
    });
}

function handleCategorySubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const categoria = {
        nome: formData.get('nome'),
        descricao: formData.get('descricao')
    };
    fetch('/api/categorias', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(categoria)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Categoria cadastrada com sucesso!', 'success');
            closeModal('category-modal');
            refreshAppData();
        } else {
            showToast(data.message || 'Erro ao cadastrar categoria', 'error');
        }
    })
    .catch(err => {
        showToast('Erro ao cadastrar categoria', 'error');
        console.error('❌ handleCategorySubmit erro:', err);
    });
}

function handleMovementSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const movimento = {
        produto_id: parseInt(formData.get('produto_id')),
        tipo: formData.get('tipo'),
        quantidade: parseInt(formData.get('quantidade')),
        motivo: formData.get('motivo'),
        observacoes: formData.get('observacoes'),
        usuario: 'Admin'
    };

    // Logar o payload antes de enviar
    console.log('📦 Payload enviado:', movimento);

    // Validar campos obrigatórios
    if (!movimento.produto_id || isNaN(movimento.produto_id)) {
        showToast('Produto inválido!', 'error');
        return;
    }
    if (!movimento.tipo || !['entrada', 'saida'].includes(movimento.tipo)) {
        showToast('Tipo de movimentação inválido!', 'error');
        return;
    }
    if (!movimento.quantidade || isNaN(movimento.quantidade)) {
        showToast('Quantidade inválida!', 'error');
        return;
    }
    if (!movimento.motivo || typeof movimento.motivo !== 'string') {
        showToast('Motivo inválido!', 'error');
        return;
    }

    fetch('/api/movimentacoes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(movimento)
    })
    .then(async res => {
        let responseBody;
        try {
            responseBody = await res.json();
        } catch (err) {
            console.error('❌ Resposta não é JSON:', err);
            showToast('Erro inesperado no servidor. Verifique os logs.', 'error');
            return;
        }

        // Logar a resposta do backend
        console.log('🔄 Resposta do backend:', res.status, responseBody);

        if (!res.ok) {
            showToast(`Erro: ${responseBody.message || 'Erro desconhecido'}`, 'error');
            return;
        }

        showToast('Movimentação registrada com sucesso!', 'success');
        closeModal('movement-modal');
        refreshAppData();
        console.log('🟢 handleMovementSubmit OK');
    })
    .catch(err => {
        showToast('Erro ao registrar movimentação', 'error');
        console.error('❌ handleMovementSubmit erro:', err);
    });
}

// Filtros
function initFilters() {
    // Filtros de produtos
    document.getElementById('searchInput')?.addEventListener('input', applyProductFilters);
    document.getElementById('filtroCategoria')?.addEventListener('change', applyProductFilters);
    document.getElementById('filtroQuantidade')?.addEventListener('change', applyProductFilters);
    document.getElementById('filtroStatus')?.addEventListener('change', applyProductFilters);
    document.getElementById('limparFiltros')?.addEventListener('click', clearProductFilters);
    
    // Filtros de validades
    document.getElementById('validityDaysFilter')?.addEventListener('change', function() {
        const customGroup = document.getElementById('customDaysGroup');
        if (this.value === 'custom') {
            customGroup.style.display = 'block';
        } else {
            customGroup.style.display = 'none';
        }
        filterValidityProducts();
    });
    
    document.getElementById('customDays')?.addEventListener('input', filterValidityProducts);

    // Filtros de movimentações
    document.getElementById('filtroMovimentoProduto')?.addEventListener('change', applyMovementFilters);
    document.getElementById('filtroMovimentoTipo')?.addEventListener('change', applyMovementFilters);
    document.getElementById('filtroMovimentoMotivo')?.addEventListener('change', applyMovementFilters);
    document.getElementById('filtroMovimentoDataInicio')?.addEventListener('change', applyMovementFilters);
    document.getElementById('filtroMovimentoDataFim')?.addEventListener('change', applyMovementFilters);
    document.getElementById('filtroMovimentoUsuario')?.addEventListener('input', applyMovementFilters);
}

function filterProducts() {
    applyProductFilters();
}

function filterValidityProducts() {
    const filter = document.getElementById('validityDaysFilter')?.value || '';
    const customDays = document.getElementById('customDays')?.value || '';
    
    const tbody = document.getElementById('validity-table-body');
    if (!tbody) return;
    
    const rows = tbody.querySelectorAll('tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const diasRestantes = parseInt(cells[4]?.textContent) || 0;
        
        let show = true;
        
        if (filter === 'vencido') {
            show = diasRestantes < 0;
        } else if (filter === '7') {
            show = diasRestantes >= 0 && diasRestantes <= 7;
        } else if (filter === '30') {
            show = diasRestantes > 7 && diasRestantes <= 30;
        } else if (filter === 'custom' && customDays) {
            show = diasRestantes <= parseInt(customDays);
        }
        
        row.style.display = show ? '' : 'none';
    });
}

function limparFiltros() {
    clearProductFilters();
}

// Busca global
function initGlobalSearch() {
    document.getElementById('globalSearch')?.addEventListener('input', function() {
        const search = this.value.toLowerCase();
        
        if (appState.currentView === 'products-view') {
            document.getElementById('searchInput').value = search;
            filterProducts();
        }
    });
}

// Relatórios
function generateReport(type, format) {
    showToast(`Gerando relatório ${type} em formato ${format}...`, 'info');
    fetch(`/api/relatorio?type=${type}&format=${format}`)
        .then(async res => {
            if (!res.ok) {
                showToast('Erro ao gerar relatório', 'error');
                return;
            }
            const blob = await res.blob();
            // Extrair nome sugerido do header ou usar padrão
            let filename = '';
            const disposition = res.headers.get('content-disposition');
            if (disposition && disposition.indexOf('filename=') !== -1) {
                filename = disposition.split('filename=')[1].replace(/['"]/g, '');
            } else {
                filename = `relatorio_ong.${format}`;
            }
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            setTimeout(() => {
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }, 100);
            showToast(`Relatório ${type} gerado com sucesso!`, 'success');
        })
        .catch(err => {
            showToast('Erro ao gerar relatório', 'error');
            console.error('❌ generateReport erro:', err);
        });
}

// Ações de produtos
function editProduct(id) {
    const produto = appState.produtos.find(p => p.id === id);
    if (produto) {
        // Preencher formulário com dados do produto
        document.getElementById('product-name').value = produto.nome;
        document.getElementById('product-description').value = produto.descricao || '';
        document.getElementById('product-quantity').value = produto.quantidade_atual;
        document.getElementById('product-unit').value = produto.unidade;
        document.getElementById('product-expiry').value = produto.data_validade;
        document.getElementById('product-value').value = produto.valor_unitario;
        document.getElementById('product-category').value = produto.categoria_id;
        document.getElementById('product-location').value = produto.localizacao || '';
        document.getElementById('product-barcode').value = produto.codigo_barras || '';
        
        document.getElementById('product-modal-title').textContent = 'Editar Produto';
        openModal('product-modal');
    }
}

function deleteProduct(id) {
    if (confirm('Tem certeza que deseja excluir este produto?')) {
        fetch(`/api/produtos/${id}`, {
            method: 'DELETE'
        })
        .then(async response => {
            const contentType = response.headers.get('content-type') || '';
            let data = {};
            if (contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();
                data = { success: false, message: text };
            }
            if (data.success) {
                showToast('Produto excluído com sucesso!', 'success');
                refreshAppData();
            } else {
                showToast(data.message || 'Erro ao excluir produto', 'error');
            }
        })
        .catch(err => {
            showToast('Erro ao excluir produto', 'error');
            console.error('❌ deleteProduct erro:', err);
        });
    }
}

// Ações de categorias
function editCategory(id) {
    const categoria = appState.categorias.find(c => c.id === id);
    if (categoria) {
        document.getElementById('category-name').value = categoria.nome;
        document.getElementById('category-description').value = categoria.descricao || '';
        
        document.getElementById('category-modal-title').textContent = 'Editar Categoria';
        openModal('category-modal');
    }
}

function deleteCategory(id) {
    if (confirm('Tem certeza que deseja excluir esta categoria?')) {
        fetch(`/api/categorias/${id}`, {
            method: 'DELETE'
        })
        .then(async response => {
            const contentType = response.headers.get('content-type') || '';
            let data = {};
            if (contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();
                data = { success: false, message: text };
            }
            if (data.success) {
                showToast('Categoria excluída com sucesso!', 'success');
                refreshAppData();
            } else {
                showToast(data.message || 'Erro ao excluir categoria', 'error');
            }
        })
        .catch(err => {
            showToast('Erro ao excluir categoria', 'error');
            console.error('❌ deleteCategory erro:', err);
        });
    }
}

// Ações de movimentações
function editMovement(id) {
    const mov = appState.movimentacoes.find(m => m.id === id);
    if (mov) {
        document.getElementById('movement-date').value = mov.data_movimentacao;
        document.getElementById('movement-product').value = mov.produto_id;
        document.getElementById('movement-type').value = mov.tipo;
        document.getElementById('movement-quantity').value = mov.quantidade;
        document.getElementById('movement-motive').value = mov.motivo || '';
        document.getElementById('movement-user').value = mov.usuario || '';
        document.getElementById('movement-modal-title').textContent = 'Editar Movimentação';
        openModal('movement-modal');
        // Armazenar o id para salvar depois
        appState.editingMovementId = id;
    } else {
        showToast('Movimentação não encontrada', 'error');
    }
}

function deleteMovement(id) {
    if (confirm('Tem certeza que deseja excluir esta movimentação?')) {
        fetch(`/api/movimentacoes/${id}`, {
            method: 'DELETE'
        })
        .then(async response => {
            const contentType = response.headers.get('content-type') || '';
            let data = {};
            if (contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();
                data = { success: false, message: text };
            }
            if (data.success) {
                showToast('Movimentação excluída com sucesso!', 'success');
                refreshAppData();
            } else {
                showToast(data.message || 'Erro ao excluir movimentação', 'error');
            }
        })
        .catch(err => {
            showToast('Erro ao excluir movimentação', 'error');
            console.error('❌ deleteMovement erro:', err);
        });
    }
}

// Utilitários
function getValidityStatus(dias) {
    if (dias < 0) return 'vencido';   // 🔴 Vermelho
    if (dias <= 7) return 'urgente';  // 🟡 Amarelo (#f59e0b)
    return 'ok';                      // 🟢 Verde
}

function getStatusText(status) {
    const texts = {
        'vencido': 'Vencido',
        'urgente': 'Vencem em 7 dias',  // Atualizado
        'ok': 'Vencem em 30 dias'
    };
    return texts[status] || 'N/A';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function getCategoryName(id) {
    const categoria = appState.categorias.find(c => c.id === parseInt(id));
    return categoria ? categoria.nome : 'N/A';
}

function matchQuantityFilter(text, filter) {
    const quantity = parseInt(text);
    switch(filter) {
        case 'baixa': return quantity < 10;
        case 'media': return quantity >= 10 && quantity <= 50;
        case 'alta': return quantity > 50;
        default: return true;
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    // Mostrar toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Remover toast após 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Exportar funções globais
window.toggleSidebar = toggleSidebar;
window.showView = showView;
window.openModal = openModal;
window.closeModal = closeModal;
window.limparFiltros = limparFiltros;
window.generateReport = generateReport;
window.editProduct = editProduct;
window.deleteProduct = deleteProduct;
window.editCategory = editCategory;
window.deleteCategory = deleteCategory;
window.editMovement = editMovement;
window.deleteMovement = deleteMovement;
