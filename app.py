from modules import api_router, plot_router, web_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import matplotlib
# Используем не-интерактивный backend для matplotlib (если понадобится)
matplotlib.use('Agg')


app = FastAPI(title="LeetCode Progress Tracker",
              description="Отслеживание прогресса на LeетCode")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутеры
app.include_router(web_router)
app.include_router(api_router)
app.include_router(plot_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
