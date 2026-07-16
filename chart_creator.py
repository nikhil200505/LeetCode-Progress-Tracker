"""Модуль для создания интерактивных графиков с помощью ApexCharts.js."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
from datetime import datetime
from config import FIGURE_SIZE, PLOT_STYLE, MARKER_SIZE, TITLE_FONT_SIZE, AXIS_FONT_SIZE, LEGEND_FONT_SIZE
from modules.i18n import i18n

# Константы для аннотаций
ANNOTATION_X_OFFSET_PERCENT = 0.03  # 3% от временного диапазона для смещения аннотации по X
ANNOTATION_Y_OFFSET_BASE = -15  # Базовое смещение по Y для аннотаций
ANNOTATION_Y_OFFSET_STEP = 18  # Шаг смещения для избежания пересечений


def _create_username_annotations(df, series):
    """Создает аннотации с именами пользователей над конечными точками линий графика."""
    annotations = []
    
    # Ограничиваем количество аннотаций, чтобы не загромождать график
    max_annotations = 8
    series_to_annotate = series[:max_annotations] if len(series) > max_annotations else series
    
    for i, serie in enumerate(series_to_annotate):
        username = serie['name']
        data_points = serie['data']
        
        if not data_points:
            continue
            
        # Берем последнюю точку для размещения подписи, но смещаем по X назад
        last_point = data_points[-1]
        
        # Вычисляем смещение по X (используем константу для процента от временного диапазона)
        if len(data_points) > 1:
            time_range = data_points[-1]['x'] - data_points[0]['x']
            x_offset = time_range * ANNOTATION_X_OFFSET_PERCENT
            annotation_x = last_point['x'] - x_offset
        else:
            annotation_x = last_point['x']
        
        # Динамическое смещение для избежания пересечений
        offset_y = ANNOTATION_Y_OFFSET_BASE - (i * ANNOTATION_Y_OFFSET_STEP)
        
        # Создаем аннотацию для имени пользователя
        annotation = {
            'x': annotation_x,
            'y': last_point['y'],
            'marker': {
                'size': 0  # Скрываем маркер аннотации
            },
            'label': {
                'text': username,
                'offsetY': offset_y,
                'offsetX': -10,  # Небольшое дополнительное смещение влево
                'style': {
                    'background': '#fff',
                    'color': '#333',
                    'fontSize': '12px',
                    'fontWeight': 'bold',
                    'textAnchor': 'middle',
                    'padding': {
                        'left': 5,
                        'right': 5,
                        'top': 2,
                        'bottom': 2
                    },
                    'border': {
                        'color': '#ccc',
                        'width': 1
                    }
                }
            }
        }
        annotations.append(annotation)
    
    return annotations


def _create_difficulty_annotations(series_list):
    """Создает аннотации для графиков уровней сложности с несколькими сериями."""
    annotations = []
    
    for i, serie in enumerate(series_list):
        serie_name = serie['name']
        data_points = serie['data']
        
        if not data_points:
            continue
            
        # Берем последнюю точку для размещения подписи, но смещаем по X назад
        last_point = data_points[-1]
        
        # Вычисляем смещение по X (используем константу для процента от временного диапазона)
        if len(data_points) > 1:
            time_range = data_points[-1]['x'] - data_points[0]['x']
            x_offset = time_range * ANNOTATION_X_OFFSET_PERCENT
            annotation_x = last_point['x'] - x_offset
        else:
            annotation_x = last_point['x']
        
        # Динамическое смещение для избежания пересечений
        offset_y = ANNOTATION_Y_OFFSET_BASE - (i * ANNOTATION_Y_OFFSET_STEP)
        
        # Создаем аннотацию для названия серии
        annotation = {
            'x': annotation_x,
            'y': last_point['y'],
            'marker': {
                'size': 0  # Скрываем маркер аннотации
            },
            'label': {
                'text': serie_name,
                'offsetY': offset_y,
                'offsetX': -15,  # Небольшое дополнительное смещение влево
                'style': {
                    'background': serie.get('color', '#333'),
                    'color': '#fff',
                    'fontSize': '11px',
                    'fontWeight': 'bold',
                    'textAnchor': 'middle',
                    'padding': {
                        'left': 4,
                        'right': 4,
                        'top': 2,
                        'bottom': 2
                    }
                }
            }
        }
        annotations.append(annotation)
    
    return annotations


def create_progress_plot_data(df, language="ru"):
    """Создает конфигурацию для интерактивного графика прогресса с ApexCharts."""
    # Устанавливаем язык для переводов
    i18n.set_language(language)

    series = []

    for username in df.columns:
        # Убираем NaN значения для корректного отображения
        clean_data = df[username].dropna()
        if not clean_data.empty:
            # Подготавливаем данные для ApexCharts
            data_points = []
            for timestamp, value in clean_data.items():
                data_points.append({
                    # Timestamp в миллисекундах
                    'x': int(timestamp.timestamp() * 1000),
                    'y': float(value)
                })

            series.append({
                'name': str(username),
                'data': data_points
            })

    # Конфигурация для ApexCharts
    chart_config = {
        'chart': {
            'type': 'line',
            'height': 500,
            'toolbar': {
                'show': True
            },
            'animations': {
                'enabled': True,
                'easing': 'easeinout',
                'speed': 800,
                'animateGradually': {
                    'enabled': True,
                    'delay': 100
                },
                'dynamicAnimation': {
                    'enabled': True,
                    'speed': 350
                }
            }
        },
        'series': series,
        'xaxis': {
            'type': 'datetime',
            'title': {
                'text': i18n.translate('charts.axes.date_time')
            }
        },
        'yaxis': {
            'title': {
                'text': i18n.translate('charts.axes.solved_relative')
            }
        },
        'title': {
            'text': i18n.translate('charts.progress_title'),
            'align': 'center'
        },
        'stroke': {
            'width': 2,
            'curve': 'smooth'
        },
        'markers': {
            'size': 4
        },
        'tooltip': {
            'x': {
                'format': 'dd/MM/yyyy HH:mm'
            }
        },
        'legend': {
            'position': 'top'
        },
        'annotations': {
            'points': _create_username_annotations(df, series)
        }
    }

    return chart_config


def create_total_plot_data(df, language="ru"):
    """Создает конфигурацию для интерактивного графика общего количества задач с ApexCharts."""
    # Устанавливаем язык для переводов
    i18n.set_language(language)

    series = []

    for username in df.columns:
        # Убираем NaN значения для корректного отображения
        clean_data = df[username].dropna()
        if not clean_data.empty:
            # Подготавливаем данные для ApexCharts
            data_points = []
            for timestamp, value in clean_data.items():
                data_points.append({
                    # Timestamp в миллисекундах
                    'x': int(timestamp.timestamp() * 1000),
                    'y': float(value)
                })

            series.append({
                'name': str(username),
                'data': data_points
            })

    # Конфигурация для ApexCharts
    chart_config = {
        'chart': {
            'type': 'line',
            'height': 500,
            'toolbar': {
                'show': True
            },
            'animations': {
                'enabled': True,
                'easing': 'easeinout',
                'speed': 800,
                'animateGradually': {
                    'enabled': True,
                    'delay': 100
                },
                'dynamicAnimation': {
                    'enabled': True,
                    'speed': 350
                }
            }
        },
        'series': series,
        'xaxis': {
            'type': 'datetime',
            'title': {
                'text': i18n.translate('charts.axes.date_time')
            }
        },
        'yaxis': {
            'title': {
                'text': i18n.translate('charts.axes.total_solved')
            }
        },
        'title': {
            'text': i18n.translate('charts.total_title'),
            'align': 'center'
        },
        'stroke': {
            'width': 2,
            'curve': 'smooth'
        },
        'markers': {
            'size': 4
        },
        'tooltip': {
            'x': {
                'format': 'dd/MM/yyyy HH:mm'
            }
        },
        'legend': {
            'position': 'top'
        },
        'annotations': {
            'points': _create_username_annotations(df, series)
        }
    }

    return chart_config


def create_difficulty_breakdown_data(
        df_easy, df_medium, df_hard, language="ru"):
    """Создает конфигурацию для интерактивного графика распределения задач по уровням сложности."""
    # Устанавливаем язык для переводов
    i18n.set_language(language)

    categories = []
    easy_data = []
    medium_data = []
    hard_data = []

    for username in df_easy.columns:
        if username in df_medium.columns and username in df_hard.columns:
            categories.append(str(username))

            # Данные для последнего замера
            latest_easy = df_easy[username].dropna(
            ).iloc[-1] if not df_easy[username].dropna().empty else 0
            latest_medium = df_medium[username].dropna(
            ).iloc[-1] if not df_medium[username].dropna().empty else 0
            latest_hard = df_hard[username].dropna(
            ).iloc[-1] if not df_hard[username].dropna().empty else 0

            easy_data.append(float(latest_easy))
            medium_data.append(float(latest_medium))
            hard_data.append(float(latest_hard))

    # Конфигурация для ApexCharts
    chart_config = {
        'chart': {
            'type': 'bar',
            'height': 500,
            'stacked': True,
            'toolbar': {
                'show': True
            },
            'animations': {
                'enabled': True,
                'easing': 'easeinout',
                'speed': 800,
                'animateGradually': {
                    'enabled': True,
                    'delay': 150
                },
                'dynamicAnimation': {
                    'enabled': True,
                    'speed': 350
                }
            }
        },
        'series': [
            {
                'name': i18n.translate('charts.series_labels.easy'),
                'data': easy_data,
                'color': '#4CAF50'
            },
            {
                'name': i18n.translate('charts.series_labels.medium'),
                'data': medium_data,
                'color': '#FF9800'
            },
            {
                'name': i18n.translate('charts.series_labels.hard'),
                'data': hard_data,
                'color': '#F44336'
            }
        ],
        'xaxis': {
            'categories': categories,
            'title': {
                'text': i18n.translate('charts.axes.users')
            }
        },
        'yaxis': {
            'title': {
                'text': i18n.translate('charts.axes.tasks_count')
            }
        },
        'title': {
            'text': i18n.translate('charts.difficulty_breakdown_title'),
            'align': 'center'
        },
        'legend': {
            'position': 'top'
        },
        'plotOptions': {
            'bar': {
                'horizontal': False
            }
        }
    }

    return chart_config


def create_daily_progress_data(data_dict, language="ru"):
    """Создает конфигурацию для графика прогресса с группировкой по дням."""
    # Устанавливаем язык для переводов
    i18n.set_language(language)

    df_total = data_dict['total']

    if df_total.empty:
        return {'series': [], 'chart': {'type': 'line'}}

    # Группируем по дням
    df_daily = df_total.groupby(df_total.index.date).last()
    df_daily.index = pd.to_datetime(df_daily.index)

    series = []

    for username in df_daily.columns:
        clean_data = df_daily[username].dropna()
        if not clean_data.empty:
            data_points = []
            for timestamp, value in clean_data.items():
                data_points.append({
                    'x': int(timestamp.timestamp() * 1000),
                    'y': float(value)
                })

            series.append({
                'name': str(username),
                'data': data_points
            })

    chart_config = {
        'chart': {
            'type': 'line',
            'height': 500,
            'toolbar': {
                'show': True
            },
            'animations': {
                'enabled': True,
                'easing': 'easeinout',
                'speed': 800,
                'animateGradually': {
                    'enabled': True,
                    'delay': 100
                },
                'dynamicAnimation': {
                    'enabled': True,
                    'speed': 350
                }
            }
        },
        'series': series,
        'xaxis': {
            'type': 'datetime',
            'title': {
                'text': i18n.translate('charts.axes.date')
            }
        },
        'yaxis': {
            'title': {
                'text': i18n.translate('charts.axes.total_solved')
            }
        },
        'title': {
            'text': i18n.translate('charts.daily_title'),
            'align': 'center'
        },
        'stroke': {
            'width': 2,
            'curve': 'smooth'
        },
        'markers': {
            'size': 6
        },
        'tooltip': {
            'x': {
                'format': 'dd/MM/yyyy'
            }
        },
        'legend': {
            'position': 'top'
        },
        'annotations': {
            'points': _create_username_annotations(df_daily, series)
        }
    }

    return chart_config


def create_difficulty_total_data(df_easy, df_medium, df_hard, language="ru"):
    """Создает конфигурацию для графика общего количества задач по каждому уровню сложности."""
    # Устанавливаем язык для переводов
    i18n.set_language(language)

    series = []

    colors = {
        'easy': '#4CAF50',
        'medium': '#FF9800',
        'hard': '#F44336'
    }

    # Добавляем данные для каждого уровня сложности
    difficulty_data = [
        (df_easy, 'Easy', colors['easy']),
        (df_medium, 'Medium', colors['medium']),
        (df_hard, 'Hard', colors['hard'])
    ]

    for df, level, color in difficulty_data:
        if not df.empty:
            for username in df.columns:
                clean_data = df[username].dropna()
                if not clean_data.empty:
                    data_points = []
                    for timestamp, value in clean_data.items():
                        data_points.append({
                            'x': int(timestamp.timestamp() * 1000),
                            'y': float(value)
                        })

                    series.append({
                        'name': f'{username} ({level})',
                        'data': data_points,
                        'color': color
                    })

    chart_config = {
        'chart': {
            'type': 'line',
            'height': 600,
            'toolbar': {
                'show': True
            },
            'animations': {
                'enabled': True,
                'easing': 'easeinout',
                'speed': 800,
                'animateGradually': {
                    'enabled': True,
                    'delay': 120
                },
                'dynamicAnimation': {
                    'enabled': True,
                    'speed': 350
                }
            }
        },
        'series': series,
        'xaxis': {
            'type': 'datetime',
            'title': {
                'text': i18n.translate('charts.axes.date_time')
            }
        },
        'yaxis': {
            'title': {
                'text': i18n.translate('charts.axes.total_solved')
            }
        },
        'title': {
            'text': i18n.translate('charts.difficulty_total_title'),
            'align': 'center'
        },
        'stroke': {
            'width': 2,
            'curve': 'smooth'
        },
        'markers': {
            'size': 4
        },
        'tooltip': {
            'x': {
                'format': 'dd/MM/yyyy HH:mm'
            }
        },
        'legend': {
            'position': 'top',
            'onItemClick': {
                'toggleDataSeries': False
            }
        },
        'annotations': {
            'points': _create_difficulty_annotations(series)
        }
    }

    return chart_config


def create_difficulty_progress_data(
        df_progress_easy, df_progress_medium, df_progress_hard, language="ru"):
    """Создает конфигурацию для графика прогресса по каждому уровню сложности."""
    # Устанавливаем язык для переводов
    i18n.set_language(language)

    series = []

    colors = {
        'easy': '#4CAF50',
        'medium': '#FF9800',
        'hard': '#F44336'
    }

    # Добавляем данные для каждого уровня сложности
    difficulty_data = [
        (df_progress_easy, 'Easy', colors['easy']),
        (df_progress_medium, 'Medium', colors['medium']),
        (df_progress_hard, 'Hard', colors['hard'])
    ]

    for df, level, color in difficulty_data:
        if not df.empty:
            for username in df.columns:
                clean_data = df[username].dropna()
                if not clean_data.empty:
                    data_points = []
                    for timestamp, value in clean_data.items():
                        data_points.append({
                            'x': int(timestamp.timestamp() * 1000),
                            'y': float(value)
                        })

                    series.append({
                        'name': f'{username} ({level})',
                        'data': data_points,
                        'color': color
                    })

    chart_config = {
        'chart': {
            'type': 'line',
            'height': 600,
            'toolbar': {
                'show': True
            },
            'animations': {
                'enabled': True,
                'easing': 'easeinout',
                'speed': 800,
                'animateGradually': {
                    'enabled': True,
                    'delay': 120
                },
                'dynamicAnimation': {
                    'enabled': True,
                    'speed': 350
                }
            }
        },
        'series': series,
        'xaxis': {
            'type': 'datetime',
            'title': {
                'text': i18n.translate('charts.axes.date_time')
            }
        },
        'yaxis': {
            'title': {
                'text': i18n.translate('charts.axes.progress_relative')
            }
        },
        'title': {
            'text': i18n.translate('charts.difficulty_progress_title'),
            'align': 'center'
        },
        'stroke': {
            'width': 2,
            'curve': 'smooth'
        },
        'markers': {
            'size': 4
        },
        'tooltip': {
            'x': {
                'format': 'dd/MM/yyyy HH:mm'
            }
        },
        'legend': {
            'position': 'top',
            'onItemClick': {
                'toggleDataSeries': False
            }
        },
        'annotations': {
            'points': _create_difficulty_annotations(series)
        }
    }

    return chart_config


def create_weekly_heatmap_data(data_dict, language="ru"):
    """Создает конфигурацию для тепловой карты активности по дням недели и часам."""
    # Устанавливаем язык для переводов
    i18n.set_language(language)

    df_total = data_dict['total']

    if df_total.empty:
        return {'series': [], 'chart': {'type': 'heatmap'}}

    # Создаем DataFrame для всех пользователей с временными метками
    activity_data = []

    for username in df_total.columns:
        user_data = df_total[username].dropna()
        if not user_data.empty:
            # Вычисляем разности (активность)
            activity = user_data.diff().fillna(0)
            activity = activity[activity > 0]  # Только положительные изменения

            for timestamp, value in activity.items():
                activity_data.append({
                    'username': username,
                    'timestamp': timestamp,
                    'activity': value,
                    'hour': timestamp.hour,
                    'day_of_week': timestamp.strftime('%A'),
                    'weekday': timestamp.weekday()
                })

    if not activity_data:
        return {'series': [], 'chart': {'type': 'heatmap'}}

    activity_df = pd.DataFrame(activity_data)

    # Группируем по дням недели и часам
    heatmap_data = activity_df.groupby(['day_of_week', 'weekday', 'hour'])[
        'activity'].sum().reset_index()

    # Создаем серии данных для тепловой карты
    days_order = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday']
    series = []

    for day in days_order:
        day_data = []
        for hour in range(24):
            activity = heatmap_data[
                (heatmap_data['day_of_week'] == day) &
                (heatmap_data['hour'] == hour)
            ]['activity'].sum()
            day_data.append({
                'x': f'{hour}:00',
                'y': float(activity)
            })

        series.append({
            'name': day,
            'data': day_data
        })

    chart_config = {
        'chart': {
            'type': 'heatmap',
            'height': 400,
            'toolbar': {
                'show': True
            },
            'animations': {
                'enabled': True,
                'easing': 'easeinout',
                'speed': 1000,
                'animateGradually': {
                    'enabled': True,
                    'delay': 200
                },
                'dynamicAnimation': {
                    'enabled': True,
                    'speed': 400
                }
            }
        },
        'series': series,
        'xaxis': {
            'title': {
                'text': i18n.translate('charts.axes.hour_of_day')
            }
        },
        'yaxis': {
            'title': {
                'text': i18n.translate('charts.axes.day_of_week')
            }
        },
        'title': {
            'text': i18n.translate('charts.heatmap_title'),
            'align': 'center'
        },
        'plotOptions': {
            'heatmap': {
                'shadeIntensity': 0.5,
                'colorScale': {
                    'ranges': [{
                        'from': 0,
                        'to': 5,
                        'name': 'низкая',
                        'color': '#FFF3E0'
                    }, {
                        'from': 6,
                        'to': 20,
                        'name': 'средняя',
                        'color': '#FF9800'
                    }, {
                        'from': 21,
                        'to': 50,
                        'name': 'высокая',
                        'color': '#F57C00'
                    }]
                }
            }
        }
    }

    return chart_config


def create_progress_plot(df):
    """Создает график прогресса и возвращает его в виде байтов."""
    plt.style.use(PLOT_STYLE)
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    for username in df.columns:
        ax.plot(
            df.index,
            df[username],
            marker='o',
            linestyle='-',
            markersize=MARKER_SIZE,
            label=username)

    ax.set_title(
        'Прогресс на LeetCode (с начала отслеживания)',
        fontsize=TITLE_FONT_SIZE,
        pad=20)
    ax.set_xlabel('Дата и время', fontsize=AXIS_FONT_SIZE)
    ax.set_ylabel(
        'Решено задач (относительно старта)',
        fontsize=AXIS_FONT_SIZE)
    ax.legend(title='Участники', fontsize=LEGEND_FONT_SIZE)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Улучшенное форматирование оси X
    fig.autofmt_xdate(rotation=30, ha='right')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    plt.tight_layout()

    # Сохраняем график в BytesIO
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=150)
    img.seek(0)
    plt.close()  # Важно закрыть фигуру для освобождения памяти

    return img


def create_total_plot(df):
    """Создает график общего количества решенных задач."""
    plt.style.use(PLOT_STYLE)
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    for username in df.columns:
        ax.plot(
            df.index,
            df[username],
            marker='o',
            linestyle='-',
            markersize=MARKER_SIZE,
            label=username)

    ax.set_title(
        'Общее количество решенных задач на LeetCode',
        fontsize=TITLE_FONT_SIZE,
        pad=20)
    ax.set_xlabel('Дата и время', fontsize=AXIS_FONT_SIZE)
    ax.set_ylabel('Общее количество решенных задач', fontsize=AXIS_FONT_SIZE)
    ax.legend(title='Участники', fontsize=LEGEND_FONT_SIZE)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Улучшенное форматирование оси X
    fig.autofmt_xdate(rotation=30, ha='right')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    plt.tight_layout()

    # Сохраняем график в BytesIO
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=150)
    img.seek(0)
    plt.close()

    return img
