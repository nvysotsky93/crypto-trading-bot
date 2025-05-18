def format_signal(data):
    msg = (
        f"Сигнал по {data['symbol']} ({data['time']} UTC):\n"
        f"Цена: {data['price']}\n"
        f"Сигнал: {data['signal']} (оценка: {data['score']})\n\n"
        f"Обоснование:\n- " + "\n- ".join(data['reasons'])
    )
    return msg
