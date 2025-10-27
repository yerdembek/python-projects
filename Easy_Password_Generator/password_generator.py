import argparse
import secrets
import string
import math

try:
    import pyperclip
    _HAS_PYPERCLIP = True
except Exception:
    _HAS_PYPERCLIP = False

SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/|~"

def build_charset(use_lower=True, use_upper=True, use_digits=True, use_symbols=True):
    charset = ""
    if use_lower:
        charset += string.ascii_lowercase
    if use_upper:
        charset += string.ascii_uppercase
    if use_digits:
        charset += string.digits
    if use_symbols:
        charset += SYMBOLS
    return charset

def generate_password(length: int, charset: str) -> str:
    if length <= 0:
        raise ValueError("Length must be positive")
    if not charset:
        raise ValueError("Charset is empty — enable at least one character class")
    return ''.join(secrets.choice(charset) for _ in range(length))

def entropy_bits(length: int, charset_size: int) -> float:
    if charset_size <= 1 or length <= 0:
        return 0.0
    return length * math.log2(charset_size)

def parse_args():
    p = argparse.ArgumentParser(description="Secure password generator (uses secrets).")
    p.add_argument("-l", "--length", type=int, default=16, help="Password length (default 16)")
    p.add_argument("--no-lower", action="store_true", help="Exclude lowercase letters")
    p.add_argument("--no-upper", action="store_true", help="Exclude capital letters")
    p.add_argument("--no-digits", action="store_true", help="Exclude numbers")
    p.add_argument("--no-symbols", action="store_true", help="Exclude symbols")
    p.add_argument("--copy", action="store_true", help="Copy password to clipboard (pyperclip)")
    p.add_argument("-n", "--count", type=int, default=1, help="Generate N passwords (default 1)")
    return p.parse_args()

def main():
    args = parse_args()
    use_lower = not args.no_lower
    use_upper = not args.no_upper
    use_digits = not args.no_digits
    use_symbols = not args.no_symbols

    charset = build_charset(use_lower, use_upper, use_digits, use_symbols)
    if not charset:
        print("Error: Empty character set. Please include at least one character class.")
        return

    if args.copy and not _HAS_PYPERCLIP:
        print("Pyperclip not found - the --copy option will be ignored. Install: pip install pyperclip")

    for i in range(args.count):
        pwd = generate_password(args.length, charset)
        bits = entropy_bits(args.length, len(charset))
        print(f"Password #{i+1}: {pwd}")
        print(f"Length: {args.length}, Character set: {len(charset)} chars, Entropy ≈ {bits:.1f} bit")
        print("-" * 40)
        if args.copy and i == 0 and _HAS_PYPERCLIP:
            try:
                pyperclip.copy(pwd)
                print("Copied to clipboard (first password only).")
            except Exception as e:
                print("Failed to copy to clipboard:", e)

if __name__ == "__main__":
    main()