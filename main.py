from tkinter import *
from tkinter import messagebox, Menu
import requests
import sqlite3


pycrypto = Tk()
pycrypto.title("My Crypto Portfolio")

try:
    pycrypto.iconbitmap("favicon.ico")
except:
    pass


con = sqlite3.connect("coin.db")
cursorObj = con.cursor()

cursorObj.execute("""
    CREATE TABLE IF NOT EXISTS coin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        amount REAL,
        price REAL
    )
""")

con.commit()


# -----------------------------
# RESET
# -----------------------------
def reset():
    for cell in pycrypto.winfo_children():
        cell.destroy()

    app_nav()
    app_header()
    my_portfolio()


# -----------------------------
# NAVIGATION MENU
# -----------------------------
def app_nav():

    menu = Menu(pycrypto)

    file_item = Menu(menu, tearoff=0)

    def clear_all():
        result = messagebox.askyesno(
            "Clear Portfolio",
            "Are you sure you want to clear the portfolio?"
        )

        if result:
            cursorObj.execute("DELETE FROM coin")
            con.commit()

            messagebox.showinfo(
                "Portfolio Notification",
                "Portfolio cleared - Add new coin"
            )

            reset()

    def close_app():
        pycrypto.destroy()

    file_item.add_command(
        label="Clear Portfolio",
        command=clear_all
    )

    file_item.add_command(
        label="Close App",
        command=close_app
    )

    menu.add_cascade(
        label="File",
        menu=file_item
    )

    pycrypto.config(menu=menu)


# -----------------------------
# PORTFOLIO
# -----------------------------
def my_portfolio():

    # IMPORTANT:
    # Put your NEW CoinMarketCap API key here.
    API_KEY = "YOUR_NEW_API_KEY"

    url = (
        "https://pro-api.coinmarketcap.com/v1/"
        "cryptocurrency/listings/latest"
    )

    headers = {
        "X-CMC_PRO_API_KEY": API_KEY
    }

    params = {
        "start": 1,
        "limit": 300,
        "convert": "USD"
    }

    try:
        api_request = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        api_request.raise_for_status()
        api = api_request.json()

    except requests.exceptions.RequestException as e:

        messagebox.showerror(
            "API Error",
            f"Unable to get cryptocurrency data.\n\n{e}"
        )

        return

    cursorObj.execute("SELECT * FROM coin")
    coins = cursorObj.fetchall()

    # -----------------------------
    # FONT COLOR
    # -----------------------------
    def font_color(amount):

        if amount < 0:
            return "red"
        else:
            return "green"

    # -----------------------------
    # INSERT COIN
    # -----------------------------
    def insert_coin():

        symbol = symbol_txt.get().strip().upper()

        try:
            price = float(price_txt.get())
            amount = float(amount_txt.get())
        except ValueError:

            messagebox.showerror(
                "Error",
                "Price and amount must be numbers."
            )

            return

        if not symbol:
            messagebox.showerror(
                "Error",
                "Please enter coin symbol."
            )

            return

        cursorObj.execute(
            """
            INSERT INTO coin(symbol, price, amount)
            VALUES (?, ?, ?)
            """,
            (symbol, price, amount)
        )

        con.commit()

        messagebox.showinfo(
            "Portfolio Notification",
            "Coin inserted"
        )

        reset()

    # -----------------------------
    # UPDATE COIN
    # -----------------------------
    def update_coin():

        try:
            portfolio_id = int(portid_update.get())
            price = float(price_update.get())
            amount = float(amount_update.get())
        except ValueError:

            messagebox.showerror(
                "Error",
                "ID, price and amount must be valid numbers."
            )

            return

        symbol = symbol_update.get().strip().upper()

        cursorObj.execute(
            """
            UPDATE coin
            SET symbol = ?, price = ?, amount = ?
            WHERE id = ?
            """,
            (
                symbol,
                price,
                amount,
                portfolio_id
            )
        )

        con.commit()

        messagebox.showinfo(
            "Portfolio Notification",
            "Coin updated"
        )

        reset()

    # -----------------------------
    # DELETE COIN
    # -----------------------------
    def delete_coin():

        try:
            portfolio_id = int(portid_delete.get())
        except ValueError:

            messagebox.showerror(
                "Error",
                "Please enter a valid portfolio ID."
            )

            return

        cursorObj.execute(
            "DELETE FROM coin WHERE id = ?",
            (portfolio_id,)
        )

        con.commit()

        messagebox.showinfo(
            "Portfolio Notification",
            "Coin deleted"
        )

        reset()

    # -----------------------------
    # CALCULATIONS
    # -----------------------------
    total_pl = 0
    coin_row = 1
    total_current_value = 0
    total_amount_paid = 0

    # -----------------------------
    # DISPLAY COINS
    # -----------------------------
    for coin in coins:

        for crypto in api["data"]:

            if crypto["symbol"] == coin[1]:

                total_paid = coin[2] * coin[3]

                current_price = crypto["quote"]["USD"]["price"]

                current_value = coin[2] * current_price

                pl_percoin = current_price - coin[3]

                total_pl_coin = pl_percoin * coin[2]

                total_pl += total_pl_coin

                total_current_value += current_value

                total_amount_paid += total_paid

                # -----------------------------
                # PORTFOLIO ID
                # -----------------------------
                portfolio_id = Label(
                    pycrypto,
                    text=coin[0],
                    bg="#F3F4F6",
                    fg="black",
                    font="Lato 12",
                    borderwidth=2,
                    relief="groove",
                    padx=2,
                    pady=2
                )

                portfolio_id.grid(
                    row=coin_row,
                    column=0,
                    sticky=N + S + E + W
                )

                # -----------------------------
                # COIN NAME
                # -----------------------------
                name = Label(
                    pycrypto,
                    text=crypto["symbol"],
                    bg="#F3F4F6",
                    fg="black",
                    font="Lato 12",
                    borderwidth=2,
                    relief="groove",
                    padx=2,
                    pady=2
                )

                name.grid(
                    row=coin_row,
                    column=1,
                    sticky=N + S + E + W
                )

                # -----------------------------
                # PRICE
                # -----------------------------
                price = Label(
                    pycrypto,
                    text="${:.2f}".format(current_price),
                    bg="#F3F4F6",
                    fg="black",
                    font="Lato 12",
                    borderwidth=2,
                    relief="groove",
                    padx=2,
                    pady=2
                )

                price.grid(
                    row=coin_row,
                    column=2,
                    sticky=N + S + E + W
                )

                # -----------------------------
                # COINS OWNED
                # -----------------------------
                no_coins = Label(
                    pycrypto,
                    text=coin[2],
                    bg="#F3F4F6",
                    fg="black",
                    font="Lato 12",
                    borderwidth=2,
                    relief="groove",
                    padx=2,
                    pady=2
                )

                no_coins.grid(
                    row=coin_row,
                    column=3,
                    sticky=N + S + E + W
                )

                # -----------------------------
                # AMOUNT PAID
                # -----------------------------
                amount_paid = Label(
                    pycrypto,
                    text="${:.2f}".format(total_paid),
                    bg="#F3F4F6",
                    fg="black",
                    font="Lato 12",
                    borderwidth=2,
                    relief="groove",
                    padx=2,
                    pady=2
                )

                amount_paid.grid(
                    row=coin_row,
                    column=4,
                    sticky=N + S + E + W
                )

                # -----------------------------
                # CURRENT VALUE
                # -----------------------------
                current_val = Label(
                    pycrypto,
                    text="${:.2f}".format(current_value),
                    bg="#F3F4F6",
                    fg="black",
                    font="Lato 12",
                    borderwidth=2,
                    relief="groove",
                    padx=2,
                    pady=2
                )

                current_val.grid(
                    row=coin_row,
                    column=5,
                    sticky=N + S + E + W
                )

                # -----------------------------
                # P/L PER COIN
                # -----------------------------
                pl_coin = Label(
                    pycrypto,
                    text="${:.2f}".format(pl_percoin),
                    bg="#F3F4F6",
                    fg=font_color(pl_percoin),
                    font="Lato 12",
                    borderwidth=2,
                    relief="groove",
                    padx=2,
                    pady=2
                )

                pl_coin.grid(
                    row=coin_row,
                    column=6,
                    sticky=N + S + E + W
                )

                # -----------------------------
                # TOTAL P/L
                # -----------------------------
                totalpl = Label(
                    pycrypto,
                    text="${:.2f}".format(total_pl_coin),
                    bg="#F3F4F6",
                    fg=font_color(total_pl_coin),
                    font="Lato 12",
                    borderwidth=2,
                    relief="groove",
                    padx=2,
                    pady=2
                )

                totalpl.grid(
                    row=coin_row,
                    column=7,
                    sticky=N + S + E + W
                )

                coin_row += 1

                break

    # -----------------------------
    # INSERT COIN
    # -----------------------------
    symbol_txt = Entry(
        pycrypto,
        borderwidth=2,
        relief="groove"
    )

    symbol_txt.grid(
        row=coin_row + 1,
        column=1
    )

    price_txt = Entry(
        pycrypto,
        borderwidth=2,
        relief="groove"
    )

    price_txt.grid(
        row=coin_row + 1,
        column=2
    )

    amount_txt = Entry(
        pycrypto,
        borderwidth=2,
        relief="groove"
    )

    amount_txt.grid(
        row=coin_row + 1,
        column=3
    )

    add_coin = Button(
        pycrypto,
        text="Add Coin",
        bg="#142E54",
        fg="white",
        command=insert_coin,
        font="Lato 12",
        borderwidth=2,
        relief="groove",
        padx=2,
        pady=2
    )

    add_coin.grid(
        row=coin_row + 1,
        column=4,
        sticky=N + S + E + W
    )

    # -----------------------------
    # UPDATE COIN
    # -----------------------------
    portid_update = Entry(
        pycrypto,
        borderwidth=2,
        relief="groove"
    )

    portid_update.grid(
        row=coin_row + 2,
        column=0
    )

    symbol_update = Entry(
        pycrypto,
        borderwidth=2,
        relief="groove"
    )

    symbol_update.grid(
        row=coin_row + 2,
        column=1
    )

    price_update = Entry(
        pycrypto,
        borderwidth=2,
        relief="groove"
    )

    price_update.grid(
        row=coin_row + 2,
        column=2
    )

    amount_update = Entry(
        pycrypto,
        borderwidth=2,
        relief="groove"
    )

    amount_update.grid(
        row=coin_row + 2,
        column=3
    )

    update_coin_txt = Button(
        pycrypto,
        text="Update Coin",
        bg="#142E54",
        fg="white",
        command=update_coin,
        font="Lato 12",
        borderwidth=2,
        relief="groove",
        padx=2,
        pady=2
    )

    update_coin_txt.grid(
        row=coin_row + 2,
        column=4,
        sticky=N + S + E + W
    )

    # -----------------------------
    # DELETE COIN
    # -----------------------------
    portid_delete = Entry(
        pycrypto,
        borderwidth=2,
        relief="groove"
    )

    portid_delete.grid(
        row=coin_row + 3,
        column=0
    )

    delete_coin_txt = Button(
        pycrypto,
        text="Delete Coin",
        bg="#142E54",
        fg="white",
        command=delete_coin
    )

    delete_coin_txt.grid(
        row=coin_row + 3,
        column=4,
        sticky=N + S + E + W
    )

    # -----------------------------
    # TOTALS
    # -----------------------------
    totalap = Label(
        pycrypto,
        text="${:.2f}".format(total_amount_paid),
        bg="#F3F4F6",
        fg="black",
        font="Lato 12",
        borderwidth=2,
        relief="groove",
        padx=2,
        pady=2
    )

    totalap.grid(
        row=coin_row,
        column=4,
        sticky=N + S + E + W
    )

    totalcv = Label(
        pycrypto,
        text="${:.2f}".format(total_current_value),
        bg="#F3F4F6",
        fg="black",
        font="Lato 12",
        borderwidth=2,
        relief="groove",
        padx=2,
        pady=2
    )

    totalcv.grid(
        row=coin_row,
        column=5,
        sticky=N + S + E + W
    )

    totalpl_label = Label(
        pycrypto,
        text="${:.2f}".format(total_pl),
        bg="#F3F4F6",
        fg=font_color(total_pl),
        font="Lato 12",
        borderwidth=2,
        relief="groove",
        padx=2,
        pady=2
    )

    totalpl_label.grid(
        row=coin_row,
        column=7,
        sticky=N + S + E + W
    )

    # -----------------------------
    # REFRESH
    # -----------------------------
    refresh = Button(
        pycrypto,
        text="Refresh",
        bg="#142E54",
        fg="white",
        command=reset,
        font="Lato 12",
        borderwidth=2,
        relief="groove",
        padx=2,
        pady=2
    )

    refresh.grid(
        row=coin_row + 1,
        column=7,
        sticky=N + S + E + W
    )


# -----------------------------
# HEADER
# -----------------------------
def app_header():

    headers = [
        "Portfolio ID",
        "Coin Name",
        "Price",
        "Coin Owned",
        "Total Amount Paid",
        "Current Value",
        "P/L Per Coin",
        "Total P/L With Coin"
    ]

    for column, text in enumerate(headers):

        label = Label(
            pycrypto,
            text=text,
            bg="#142E54",
            fg="white",
            font="Lato 12 bold",
            padx=5,
            pady=5,
            borderwidth=2,
            relief="groove"
        )

        label.grid(
            row=0,
            column=column,
            sticky=N + S + E + W
        )


# -----------------------------
# START APPLICATION
# -----------------------------
app_nav()
app_header()
my_portfolio()

pycrypto.mainloop()

cursorObj.close()
con.close()