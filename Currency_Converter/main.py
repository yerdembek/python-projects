import requests

PRIMARY_URL = "https://api.exchangerate.host/latest"
FALLBACK_URL = "https://api.frankfurter.app/latest"

def fetch_rates(url: str) -> dict:
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise ConnectionError(f"Provider error: HTTP {resp.status_code}")
    data = resp.json()

    if isinstance(data, dict) and data.get("success") is False:
        raise ValueError(f"Provider returned error: {data.get('error')}")
    rates = data.get("rates")
    if not isinstance(rates, dict) or "USD" not in rates:
        raise ValueError("Malformed rates data from provider.")
    rates = {k.upper(): float(v) for k, v in rates.items()}
    rates["EUR"] = 1.0
    return rates

def get_rates_with_fallback() -> dict:
    try:
        return fetch_rates(PRIMARY_URL)
    except Exception:
        return fetch_rates(FALLBACK_URL)

def compute_rate(base_currency: str, target_currency: str, rates: dict) -> float:
    base = base_currency.upper()
    target = target_currency.upper()
    if base not in rates:
        raise ValueError(f"Unknown base currency: {base}")
    if target not in rates:
        raise ValueError(f"Unknown target currency: {target}")
    return rates[target] / rates[base]

def convert_currency(amount: float, base_currency: str, target_currency: str):
    rates = get_rates_with_fallback()
    rate = compute_rate(base_currency, target_currency, rates)
    return amount * rate, rate

def main():
    print("=== 💱 Currency Converter ===")
    base = input("From currency (e.g., USD): ").strip().upper()
    target = input("To currency (e.g., EUR): ").strip().upper()

    try:
        amount = float(input("Amount: "))
    except ValueError:
        print("Error: please enter a numeric amount.")
        return

    try:
        converted, rate = convert_currency(amount, base, target)
        print(f"\nRate: 1 {base} = {rate:.4f} {target}")
        print(f"{amount} {base} = {converted:.2f} {target}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()