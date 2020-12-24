import sqlite3, config
from fastapi import FastAPI, Request, Form
from fastapi.templating  import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import date

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    stock_filter = request.query_params.get('filter', False)
    connection = sqlite3.connect(config.DB_PATH)
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row
    
    if stock_filter == 'new_closing_highs':
        cursor.execute("""SELECT * FROM (
            SELECT symbol, name, stock_id, max(close), date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            GROUP BY stock_id
            ORDER BY symbol)
            WHERE date = ?""", (date.today().isoformat(),))

    elif stock_filter == 'new_closing_lows':
        cursor.execute("""SELECT * FROM (
            SELECT symbol, name, stock_id, min(close), date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            GROUP BY stock_id
            ORDER BY symbol)
            WHERE date = ?""", (date.today().isoformat(),))

    else:
        cursor.execute("""SELECT symbol, name FROM stock ORDER BY symbol""")
    rows = cursor.fetchall()

    cursor.execute("""SELECT symbol, close, rsi_14, sma_20, sma_50, close
    FROM stock join stock_price on stock_price.stock_id = stock.id
    WHERE date IN (SELECT max(date) FROM stock_price)""")
    
    indicator_rows = cursor.fetchall()
    indicator_values = {}
    for row in indicator_rows:
        indicator_values[row[0]] = row
    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "indicators": indicator_values})


@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = sqlite3.connect(config.DB_PATH)
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row

    cursor.execute("""SELECT id,symbol, name, exchange FROM stock WHERE symbol = ?""", (symbol,))
    row = cursor.fetchone()
    cursor.execute(""" SELECT * FROM strategy""")
    strategies = cursor.fetchall()
    cursor.execute("""SELECT * FROM stock_price WHERE stock_id = ? ORDER BY date DESC""",(row[0],))
    prices = cursor.fetchall()
    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": row, "prices": prices, "strategies": strategies})


@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?, ?)
     """, (stock_id, strategy_id))
    connection.commit()
    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)

@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(""" 
    SELECT id, name
    FROM strategy
    WHERE id = ?
    """, (strategy_id,))

    strategy = cursor.fetchone()

    cursor.execute(""" 
        SELECT symbol, name
        FROM stock JOIN stock_strategy ON stock_strategy.stock_id = stock.id
        WHERE strategy_id = ?
    """, (strategy_id,))

    stocks = cursor.fetchall()

    return templates.TemplateResponse("strategy.html",{"request": request, "stocks": stocks, "strategy": strategy})