// LeetCode Progress Tracker - ApexCharts Integration

// Константы конфигурации
const CHART_LOAD_TIMEOUT = 10000; // 10 секунд
const LEGEND_CLICK_DELAY = 0; // Задержка для обновления аннотаций после клика по легенде
const ANNOTATION_UPDATE_DELAY = 0; // Задержка для обновления аннотаций

// Переводы и интернационализация
let currentTranslations = window.translations || {};
let currentLanguage = window.currentLanguage || 'ru';

// Утилитарные функции
function getErrorMessage(error) {
    // Используем систему переводов для сообщений об ошибках
    const fallbackMessage = getTranslation('errors.unknown_error') || 
                           (currentLanguage === 'en' ? 'Unknown error' : 'Неизвестная ошибка');
    
    if (currentTranslations.errors && currentTranslations.errors.unknown_error) {
        return error?.message || error?.toString() || currentTranslations.errors.unknown_error;
    }
    
    return error?.message || error?.toString() || fallbackMessage;
}

// Функция для переключения языка
async function switchLanguage(language) {
    if (!window.supportedLanguages || !window.supportedLanguages.includes(language)) {
        console.error('Неподдерживаемый язык:', language);
        return;
    }

    try {
        const response = await fetch('/api/language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `language=${language}`
        });

        if (response.ok) {
            const result = await response.json();
            
            // Обновляем переводы
            currentTranslations = result.translations;
            currentLanguage = language;
            
            // Обновляем глобальные переменные
            window.translations = result.translations;
            window.currentLanguage = language;
            
            // Обновляем переводы на странице
            updatePageTranslations();
            
            // Обновляем активную кнопку
            updateLanguageButtons(language);
            
            // Очищаем кэш графиков для перезагрузки с новыми переводами
            clearChartsCache();
            
            // Перезагружаем активный график
            const activeTab = document.querySelector('.tab-btn.active');
            if (activeTab) {
                const chartType = activeTab.dataset.chart;
                loadChart(chartType);
            }
            
            console.log('Язык успешно изменен на:', language);
        } else {
            console.error('Ошибка при смене языка:', response.statusText);
        }
    } catch (error) {
        console.error('Ошибка сети при смене языка:', error);
    }
}

// Функция для обновления переводов на странице
function updatePageTranslations() {
    const elementsToTranslate = document.querySelectorAll('[data-translate]');
    
    elementsToTranslate.forEach(element => {
        const translationKey = element.getAttribute('data-translate');
        const translation = getTranslation(translationKey);
        
        if (translation !== translationKey) {
            element.textContent = translation;
        }
    });
    
    // Обновляем заголовок документа
    document.title = getTranslation('title');
    
    // Обновляем lang атрибут HTML
    document.documentElement.lang = currentLanguage;
}

// Функция для получения перевода
function getTranslation(key) {
    const keys = key.split('.');
    let translation = currentTranslations;
    
    try {
        for (const k of keys) {
            translation = translation[k];
        }
        return translation || key;
    } catch (error) {
        return key;
    }
}

// Функция для обновления активной кнопки языка
function updateLanguageButtons(language) {
    const languageButtons = document.querySelectorAll('.language-btn');
    
    languageButtons.forEach(button => {
        button.classList.remove('active');
        // Проверяем и по тексту кнопки, и по атрибуту onclick
        const btnLang = button.textContent.includes('RU') ? 'ru' : 'en';
        if (btnLang === language || 
            button.textContent.toLowerCase().includes(language.toLowerCase()) || 
            button.getAttribute('onclick')?.includes(language)) {
            button.classList.add('active');
        }
    });
}

// Конфигурация загрузки
const loadingConfig = {
    showLoading: true,          // Показывать индикатор загрузки
    useSkeletonLoading: false,  // Использовать skeleton loading вместо спиннера (только если showLoading: true)
    preloadCharts: true,        // Предзагружать популярные графики
    fastSwitch: true,           // Быстрое переключение между табами
    preloadChartTypes: ['total', 'daily'] // Типы графиков для предзагрузки
};

// Карта соответствия endpoints и контейнеров для графиков
const chartEndpoints = {
    'progress': '/api/plot/progress',
    'total': '/api/plot/total',
    'daily': '/api/plot/daily-progress',
    'difficulty-breakdown': '/api/plot/difficulty-breakdown',
    'difficulty-total': '/api/plot/difficulty-total',
    'difficulty-progress': '/api/plot/difficulty-progress',
    'heatmap': '/api/plot/weekly-heatmap'
};

const chartContainers = {
    'progress': 'progressChart',
    'total': 'totalChart',
    'daily': 'dailyChart',
    'difficulty-breakdown': 'difficultyBreakdownChart',
    'difficulty-total': 'difficultyTotalChart',
    'difficulty-progress': 'difficultyProgressChart',
    'heatmap': 'heatmapChart'
};

// Кэш для хранения созданных диаграмм
let chartsCache = {};

// Кэш для хранения оригинальных аннотаций каждого графика
let originalAnnotations = {};

// Счетчик активных загрузок для предотвращения перегрузки сети
let activeLoadingCount = 0;
const MAX_CONCURRENT_LOADS = 2;

// Очередь ожидающих загрузки графиков
const loadQueue = [];

// Функция для безопасной загрузки с ограничением параллельных запросов
async function safeLoadChart(chartType) {
    return new Promise((resolve, reject) => {
        const loadTask = async () => {
            try {
                activeLoadingCount++;
                const result = await loadChart(chartType);
                resolve(result);
            } catch (error) {
                reject(error);
            } finally {
                activeLoadingCount--;
                processLoadQueue();
            }
        };

        if (activeLoadingCount < MAX_CONCURRENT_LOADS) {
            loadTask();
        } else {
            loadQueue.push(loadTask);
        }
    });
}

// Обработка очереди загрузки
function processLoadQueue() {
    if (loadQueue.length > 0 && activeLoadingCount < MAX_CONCURRENT_LOADS) {
        const nextTask = loadQueue.shift();
        nextTask();
    }
}

// Функция для очистки кэша графиков
function clearChartsCache() {
    // Очищаем кэш графиков для перезагрузки с новыми переводами
    Object.keys(chartsCache).forEach(chartType => {
        if (chartsCache[chartType]) {
            chartsCache[chartType].destroy();
            delete chartsCache[chartType];
        }
    });
    
    // Очищаем кэш оригинальных аннотаций
    originalAnnotations = {};
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeTabs();
    initializeTooltips();
    
    // Загружаем первый график без задержки
    const activeTab = document.querySelector('.tab-btn.active');
    let initialChartType = 'progress'; // По умолчанию
    
    if (activeTab) {
        const chartType = activeTab.dataset.chart;
        console.log('Found active tab with chart type:', chartType);
        
        // Проверяем что такой тип графика существует
        if (chartEndpoints[chartType]) {
            initialChartType = chartType;
        } else {
            console.error('Chart type not found in endpoints:', chartType);
        }
    } else {
        console.log('No active tab found, using default progress chart');
    }
    
    // Показываем контейнер и загружаем график
    showChart(initialChartType);
    loadChart(initialChartType);
    
    // Предзагружаем следующие популярные графики в фоне с небольшой задержкой
    if (loadingConfig.preloadCharts) {
        setTimeout(async () => {
            const preloadCharts = loadingConfig.preloadChartTypes || [];
            const preloadPromises = [];
            
            // Ограничиваем количество одновременных запросов
            for (const type of preloadCharts) {
                if (type !== initialChartType && chartEndpoints[type] && !chartsCache[type]) {
                    const preloadPromise = safeLoadChart(type).catch(error => {
                        console.warn(`Failed to preload chart ${type}: ${getErrorMessage(error)}`);
                        return null; // Не прерываем предзагрузку других графиков
                    });
                    preloadPromises.push(preloadPromise);
                }
            }
            
            // Ожидаем завершения всех предзагрузок
            if (preloadPromises.length > 0) {
                const results = await Promise.allSettled(preloadPromises);
                const successful = results.filter(result => result.status === 'fulfilled' && result.value !== null).length;
                console.log(`Preloaded ${successful} out of ${preloadPromises.length} charts`);
            }
        }, 500);
    }
});

// Инициализация табов
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const chartType = this.dataset.chart;
            
            // Обновляем активные табы
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Показываем соответствующий контейнер графика
            showChart(chartType);
            
            // Загружаем график если не загружен (асинхронно, не блокируя UI)
            if (!chartsCache[chartType]) {
                safeLoadChart(chartType).catch(error => {
                    console.error(`Failed to load chart ${chartType}: ${getErrorMessage(error)}`);
                });
            }
        });
    });
}

// Показать контейнер графика
function showChart(chartType) {
    const chartContainersElements = document.querySelectorAll('.chart');
    
    // Скрываем все контейнеры
    chartContainersElements.forEach(container => {
        container.classList.remove('active');
    });
    
    // Показываем нужный контейнер по составному ID (chartType + '-chart')
    const targetContainer = document.getElementById(chartType + '-chart');
    if (targetContainer) {
        targetContainer.classList.add('active');
        console.log(`Showing chart container: ${chartType}-chart`);
    } else {
        console.error(`Container ${chartType}-chart not found`);
    }
}

// Загрузка и отображение графика
async function loadChart(chartType) {
    const endpoint = chartEndpoints[chartType];
    const containerId = chartContainers[chartType];
    
    if (!endpoint || !containerId) {
        console.error(`Chart type ${chartType} not found`);
        return null;
    }
    
    // Если график уже загружен, возвращаем его сразу
    if (chartsCache[chartType]) {
        console.log(`Chart ${chartType} already cached, skipping load`);
        return chartsCache[chartType];
    }
    
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container ${containerId} not found`);
        return null;
    }
    
    try {
        // Показываем индикатор загрузки в зависимости от настроек
        if (loadingConfig.showLoading) {
            if (loadingConfig.useSkeletonLoading) {
                container.innerHTML = `
                    <div class="chart-skeleton">
                        <div class="skeleton-header"></div>
                        <div class="skeleton-chart"></div>
                    </div>
                `;
            } else {
                container.innerHTML = '<div class="chart-loading"></div>';
            }
        }
        
        // Добавляем таймаут для предотвращения долгих ожиданий
        let timeoutId;
        let response;
        
        try {
            response = await Promise.race([
                fetch(endpoint),
                new Promise((_, reject) => {
                    timeoutId = setTimeout(() => reject(new Error(`Превышено время ожидания (${CHART_LOAD_TIMEOUT / 1000} секунд)`)), CHART_LOAD_TIMEOUT);
                })
            ]);
        } finally {
            // Всегда очищаем таймер, независимо от результата
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ошибка: ${response.status} ${response.statusText}`);
        }
        
        const chartConfig = await response.json();
        
        // Очищаем контейнер от индикатора загрузки
        container.innerHTML = '';
        
        // Создаем новый график
        const chart = new ApexCharts(container, chartConfig);
        await chart.render();
        
        // Сохраняем оригинальные аннотации для последующего использования
        if (chartConfig.annotations && chartConfig.annotations.points) {
            originalAnnotations[chartType] = JSON.parse(JSON.stringify(chartConfig.annotations.points));
        }
        
        // Добавляем обработчики событий для синхронизации аннотаций с легендой
        chart.addEventListener('legendClick', function(chartContext, seriesIndex, config) {
            // Используем константу для задержки обновления аннотаций
            setTimeout(() => {
                updateAnnotationsLocally(chartType, chart);
            }, LEGEND_CLICK_DELAY);
        });
        
        // Сохраняем в кэш
        chartsCache[chartType] = chart;
        
        // Инициализируем кнопки управления для графиков уровней сложности
        if (chartType === 'difficulty-total' || chartType === 'difficulty-progress') {
            initializeDifficultyControls(chartType);
        }
        
        console.log(`Chart ${chartType} loaded successfully`);
        return chart;
    } catch (error) {
        console.error(`Error loading chart ${chartType}:`, error);
        
        const errorTitle = getTranslation('errors.chart_loading_error') || 
                          (currentLanguage === 'en' ? 'Chart loading error:' : 'Ошибка загрузки графика:');
        const retryText = getTranslation('buttons.retry') || 
                         (currentLanguage === 'en' ? '🔄 Try again' : '🔄 Попробовать снова');
        
        container.innerHTML = `
            <div class="chart-error">
                ❌ ${errorTitle} ${getErrorMessage(error)}
                <br>
                <button onclick="loadChart('${chartType}')" class="retry-btn">${retryText}</button>
            </div>
        `;
        return null;
    }
}

// Инициализация всех графиков (предзагрузка)
function initializeCharts() {
    // Инициализируем только активные вкладки при первой загрузке
    console.log('Charts initialized');
}

// Флаг для предотвращения повторной инициализации тултипов
let tooltipsInitialized = false;

// WeakMap для хранения обработчиков событий тултипов
const tooltipHandlers = new WeakMap();

// Функция для очистки тултипов (если потребуется)
function cleanupTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip="true"]');
    tooltipElements.forEach(element => {
        const handlers = tooltipHandlers.get(element);
        if (handlers) {
            element.removeEventListener('mouseenter', handlers.showTooltip);
            element.removeEventListener('mouseleave', handlers.hideTooltip);
            tooltipHandlers.delete(element);
        }
    });
    tooltipsInitialized = false;
    console.log('Tooltips cleaned up');
}

// Инициализация тултипов
function initializeTooltips() {
    // Предотвращаем повторную инициализацию
    if (tooltipsInitialized) {
        console.log('Tooltips already initialized, skipping');
        return;
    }
    
    // Добавляем обработчики для тултипов если они есть
    const tooltipElements = document.querySelectorAll('[data-tooltip="true"]');
    tooltipElements.forEach(element => {
        const tooltipContent = element.querySelector('.tooltip-content');
        if (tooltipContent) {
            // Создаем функции для обработчиков
            const showTooltip = () => {
                tooltipContent.style.display = 'block';
            };
            const hideTooltip = () => {
                tooltipContent.style.display = 'none';
            };
            
            element.addEventListener('mouseenter', showTooltip);
            element.addEventListener('mouseleave', hideTooltip);
            
            // Сохраняем ссылки на функции в WeakMap
            tooltipHandlers.set(element, { showTooltip, hideTooltip });
        }
    });
    
    tooltipsInitialized = true;
    console.log('Tooltips initialized');
}

// Обновление данных
async function updateData() {
    const updateBtn = document.getElementById('updateBtn');
    const loading = document.getElementById('loading');
    const message = document.getElementById('message');
    
    // Показываем индикатор загрузки
    updateBtn.disabled = true;
    loading.style.display = 'block';
    message.innerHTML = '';
    
    try {
        const response = await fetch('/api/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            message.innerHTML = '<p class="success">✅ ' + result.message + '</p>';
            
            // Очищаем кэш и перезагружаем текущий график
            Object.keys(chartsCache).forEach(chartType => {
                if (chartsCache[chartType]) {
                    chartsCache[chartType].destroy();
                    delete chartsCache[chartType];
                }
            });
            
            // Перезагружаем страницу для обновления статистики
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            message.innerHTML = '<p class="error">❌ ' + result.message + '</p>';
            if (result.error) {
                console.error('Update error:', result.error);
            }
        }
    } catch (error) {
        console.error('Update request failed:', error);
        const errorMsg = getTranslation('errors.network_error') || 
                        (currentLanguage === 'en' ? 'Network error:' : 'Ошибка сети:');
        message.innerHTML = `<p class="error">❌ ${errorMsg} ${error.message}</p>`;
    } finally {
        updateBtn.disabled = false;
        loading.style.display = 'none';
    }
}

// Функция для переключения видимости уровня сложности
function toggleDifficultyLevel(chartType, difficulty) {
    const chart = chartsCache[chartType];
    if (!chart) {
        console.error(`Chart ${chartType} not found in cache`);
        return;
    }
    
    const button = document.querySelector(`#${chartType}-chart .difficulty-btn[data-difficulty="${difficulty}"]`);
    if (!button) {
        console.error(`Button for difficulty ${difficulty} not found`);
        return;
    }
    
    const isActive = button.classList.contains('active');
    const difficultyLevel = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
    
    // Получаем все серии данных для данного уровня сложности
    const seriesToToggle = chart.w.globals.seriesNames.filter(name => 
        name.includes(`(${difficultyLevel})`)
    );
    
    if (isActive) {
        // Скрываем линии данного уровня сложности
        seriesToToggle.forEach(seriesName => {
            chart.hideSeries(seriesName);
        });
        button.classList.remove('active');
    } else {
        // Показываем линии данного уровня сложности
        seriesToToggle.forEach(seriesName => {
            chart.showSeries(seriesName);
        });
        button.classList.add('active');
    }
    
    // Обновляем аннотации - скрываем/показываем соответствующие подписи
    setTimeout(() => {
        updateAnnotationsLocally(chartType, chart);
    }, ANNOTATION_UPDATE_DELAY);
}

// Функция для локального обновления аннотаций без запроса к серверу
function updateAnnotationsLocally(chartType, chart) {
    const originalAnns = originalAnnotations[chartType];
    if (!originalAnns || !Array.isArray(originalAnns)) {
        return;
    }
    
    // Получаем список скрытых серий
    const hiddenSeriesIndices = chart.w.globals.collapsedSeriesIndices || [];
    const hiddenSeriesNames = hiddenSeriesIndices.map(index => 
        chart.w.globals.seriesNames[index]
    );
    
    // Для графиков с кнопками управления сложностью также проверяем их состояние
    let hiddenDifficulties = [];
    if (chartType === 'difficulty-total' || chartType === 'difficulty-progress') {
        const chartContainer = document.getElementById(`${chartType}-chart`);
        const buttons = chartContainer.querySelectorAll('.difficulty-btn');
        
        buttons.forEach(button => {
            if (!button.classList.contains('active')) {
                const difficulty = button.getAttribute('data-difficulty');
                const difficultyLevel = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
                hiddenDifficulties.push(difficultyLevel);
            }
        });
    }
    
    // Фильтруем аннотации локально
    const filteredAnnotations = originalAnns.filter(annotation => {
        // Проверяем скрытие через легенду (убираем избыточное условие)
        const isHiddenByLegend = hiddenSeriesNames.some(hiddenName => 
            annotation.label.text === hiddenName
        );
        
        // Проверяем скрытие через кнопки сложности
        const isHiddenByDifficultyButton = hiddenDifficulties.some(hiddenLevel => 
            annotation.label.text.includes(`(${hiddenLevel})`)
        );
        
        return !isHiddenByLegend && !isHiddenByDifficultyButton;
    });
    
    // Обновляем аннотации в графике напрямую
    chart.updateOptions({
        annotations: {
            points: filteredAnnotations
        }
    }, false, true); // false - не перерисовывать, true - updateSeries
}

// Функция для обновления аннотаций при переключении через легенду (устаревшая - используем updateAnnotationsLocally)
async function updateAnnotationsForLegendToggle(chartType, chart) {
    // Используем более эффективное локальное обновление
    updateAnnotationsLocally(chartType, chart);
}

// Функция для обновления видимости аннотаций на основе видимых серий
function updateAnnotationsVisibility(chart, chartType) {
    if (!chart || !originalAnnotations[chartType]) {
        return;
    }
    
    // Используем более эффективное локальное обновление
    updateAnnotationsLocally(chartType, chart);
}

// Функция для перезагрузки графика с обновленными аннотациями (рефакторена для эффективности)
async function reloadChartWithUpdatedAnnotations(chartType, visibleSeries) {
    const chart = chartsCache[chartType];
    if (!chart) {
        console.error(`Chart ${chartType} not found in cache`);
        return;
    }

    // Используем более эффективное локальное обновление вместо полной перезагрузки
    updateAnnotationsLocally(chartType, chart);
}

// Функция для инициализации кнопок управления после загрузки графика
function initializeDifficultyControls(chartType) {
    const chartContainer = document.getElementById(`${chartType}-chart`);
    if (!chartContainer) return;
    
    const controlsContainer = chartContainer.querySelector('.difficulty-controls');
    if (!controlsContainer) return;
    
    // Убеждаемся, что все кнопки изначально активны
    const buttons = controlsContainer.querySelectorAll('.difficulty-btn');
    buttons.forEach(button => {
        if (!button.classList.contains('active')) {
            button.classList.add('active');
        }
    });
}

// Обработка ошибок глобально
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// Вспомогательные функции для отладки
function debugChartData(chartType) {
    const endpoint = chartEndpoints[chartType];
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            console.log(`Chart data for ${chartType}:`, data);
        })
        .catch(error => {
            console.error(`Error fetching ${chartType} data:`, error);
        });
}

// Функция для мониторинга состояния загрузки
function getLoadingStatus() {
    return {
        activeLoadingCount,
        queueLength: loadQueue.length,
        cachedCharts: Object.keys(chartsCache),
        maxConcurrentLoads: MAX_CONCURRENT_LOADS,
        timeout: CHART_LOAD_TIMEOUT,
        config: { ...loadingConfig }
    };
}

// Функция для изменения настроек загрузки
function configureLoading(options = {}) {
    // Валидные свойства конфигурации
    const validOptions = ['showLoading', 'useSkeletonLoading', 'preloadCharts', 'fastSwitch', 'preloadChartTypes'];
    const validatedOptions = {};
    
    // Проверяем каждое переданное свойство
    for (const [key, value] of Object.entries(options)) {
        if (validOptions.includes(key)) {
            if (key === 'preloadChartTypes') {
                // Проверяем что это массив строк
                if (Array.isArray(value) && value.every(item => typeof item === 'string')) {
                    validatedOptions[key] = value;
                } else {
                    console.warn(`Invalid value type for ${key}: expected array of strings, got ${typeof value}`);
                }
            } else {
                // Проверяем тип значения (должен быть boolean для остальных свойств)
                if (typeof value === 'boolean') {
                    validatedOptions[key] = value;
                } else {
                    console.warn(`Invalid value type for ${key}: expected boolean, got ${typeof value}`);
                }
            }
        } else {
            console.warn(`Unknown configuration option: ${key}. Valid options are: ${validOptions.join(', ')}`);
        }
    }
    
    // Применяем только валидные настройки
    Object.assign(loadingConfig, validatedOptions);
    
    // Проверяем конфликты конфигурации
    if (!loadingConfig.showLoading && loadingConfig.useSkeletonLoading) {
        console.warn('Configuration conflict: useSkeletonLoading is meaningless when showLoading is false. Setting useSkeletonLoading to false.');
        loadingConfig.useSkeletonLoading = false;
    }
    
    console.log('Loading configuration updated:', loadingConfig);
    
    if (Object.keys(validatedOptions).length === 0) {
        console.warn('No valid configuration options were provided');
    }
}

// Быстрые предустановки
function disableLoading() {
    configureLoading({ showLoading: false });
}

function enableFastLoading() {
    configureLoading({ 
        showLoading: true,
        useSkeletonLoading: false,
        preloadCharts: true,
        fastSwitch: true 
    });
}

function enableSkeletonLoading() {
    configureLoading({ 
        showLoading: true,
        useSkeletonLoading: true,
        preloadCharts: true 
    });
}

// Быстрая настройка предзагружаемых графиков
function setPreloadCharts(chartTypes) {
    if (!Array.isArray(chartTypes)) {
        console.warn('setPreloadCharts expects an array of chart types');
        return;
    }
    
    const validChartTypes = chartTypes.filter(type => chartEndpoints[type]);
    if (validChartTypes.length !== chartTypes.length) {
        const invalidTypes = chartTypes.filter(type => !chartEndpoints[type]);
        console.warn('Invalid chart types ignored:', invalidTypes);
    }
    
    configureLoading({ preloadChartTypes: validChartTypes });
}

// Сброс конфигурации к безопасным значениям по умолчанию
function resetLoadingConfig() {
    loadingConfig.showLoading = true;
    loadingConfig.useSkeletonLoading = false;
    loadingConfig.preloadCharts = true;
    loadingConfig.fastSwitch = true;
    loadingConfig.preloadChartTypes = ['total', 'daily'];
    console.log('Loading configuration reset to defaults:', loadingConfig);
}

// Экспорт функций для глобального доступа
// Экспорт функций для глобального доступа
window.updateData = updateData;
window.loadChart = loadChart;
window.safeLoadChart = safeLoadChart;
window.debugChartData = debugChartData;
window.getLoadingStatus = getLoadingStatus;
window.toggleDifficultyLevel = toggleDifficultyLevel;
window.updateAnnotationsVisibility = updateAnnotationsVisibility;
window.updateAnnotationsLocally = updateAnnotationsLocally;
window.updateAnnotationsForLegendToggle = updateAnnotationsForLegendToggle;
window.reloadChartWithUpdatedAnnotations = reloadChartWithUpdatedAnnotations;
window.configureLoading = configureLoading;
window.setPreloadCharts = setPreloadCharts;
window.resetLoadingConfig = resetLoadingConfig;
window.disableLoading = disableLoading;
window.enableFastLoading = enableFastLoading;
window.enableSkeletonLoading = enableSkeletonLoading;
window.cleanupTooltips = cleanupTooltips;
window.clearChartsCache = clearChartsCache;

// Экспорт функций мультиязычности (функции определены выше)
window.switchLanguage = switchLanguage;
window.updatePageTranslations = updatePageTranslations;
window.getTranslation = getTranslation;
window.updateLanguageButtons = updateLanguageButtons;
